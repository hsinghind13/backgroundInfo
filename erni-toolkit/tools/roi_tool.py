"""
roi_tool — an interactive ROI selector for TOF stacks.

WHY THIS EXISTS
---------------
save_roi's example notebook documents an interactive selector
(`interactive.launch_interactive_tool`), but that module was never shipped:
it is absent from the PyPI package, from `main`, and from the other branch of
the repo, and there is no `[interactive]` extra declared. The only references
to it anywhere are inside that one notebook cell.

This is a replacement built on plotly's shape-drawing tools. It writes
**standard ImageJ .roi files**, so everything downstream — `load_imagej_rois`,
`get_roi_mask`, `extract_roi_spectra`, the save-roi CLI, and ImageJ itself —
consumes the output unchanged. Nothing needs to know it wasn't ImageJ.

USAGE
-----
    import roi_tool as rt

    stack = rt.load_stack("image.tiff.gz")      # handles .gz transparently
    radio = rt.radiograph(stack)                # sum over TOF

    fig = rt.make_drawer(radio)                 # draw on this
    fig                                         # <- display it

    # ...draw some shapes, then in the NEXT cell:
    rois = rt.shapes_to_rois(fig, names=["graphite", "empty"])
    rt.save_rois("my_rois.zip", rois)
    rt.check_rois("my_rois.zip", radio.shape)   # verify none are clipped

    rt.grid_preview(radio, grid_size=8)         # see your map resolution

COORDINATE CONVENTION
---------------------
Everything here is (row, col) = (y, x) with row 0 at the TOP, matching numpy
and matching how `get_roi_mask` indexes `mask[y, x]`. The plotly y-axis is
reversed for exactly this reason — without it, every ROI you draw would be
mirrored vertically relative to the mask it produces.
"""
from __future__ import annotations

import gzip
import io
import re
from pathlib import Path

import numpy as np
import pandas as pd
import roifile
import tifffile

__all__ = ["load_stack", "radiograph", "make_drawer", "shapes_to_rois",
           "save_rois", "check_rois", "grid_preview"]


# ---------------------------------------------------------------- loading ---
def load_stack(path) -> np.ndarray:
    """Load a TOF stack as (n_tof, height, width). Handles .gz transparently."""
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as fh:
            stack = tifffile.imread(io.BytesIO(fh.read()))
    else:
        stack = tifffile.imread(str(path))
    if stack.ndim == 2:
        stack = stack[np.newaxis, :, :]
    return stack


def radiograph(stack: np.ndarray) -> np.ndarray:
    """Sum over the TOF axis -> the 2D image you draw ROIs on."""
    return stack.sum(axis=0)


# ---------------------------------------------------------------- drawing ---
def make_drawer(radio: np.ndarray, *, zmax_percentile: float = 99.5,
                colorscale: str = "gray", title: str | None = None):
    """
    Return a plotly FigureWidget with rectangle / circle / freeform drawing on.

    Display it, drag out your regions, then call `shapes_to_rois(fig)` in a
    LATER cell — the shapes live in `fig.layout.shapes` and are read when that
    cell runs, so there is no callback to go wrong.

    Toolbar (top right): "Draw rectangle", "Draw circle", "Draw closed
    freeform", "Erase active shape". Click a shape to select it.
    """
    import plotly.graph_objects as go

    # Percentile clip: a few hot pixels otherwise flatten the whole image to
    # black and you cannot see the sample to draw around it.
    zmax = float(np.percentile(radio, zmax_percentile)) or float(radio.max())

    fig = go.FigureWidget(
        go.Heatmap(z=radio, colorscale=colorscale, zmin=0, zmax=zmax,
                   colorbar=dict(title="counts"))
    )
    fig.update_layout(
        title=title or f"Draw ROIs — frame {radio.shape[0]}×{radio.shape[1]}",
        dragmode="drawrect",
        newshape=dict(line_color="cyan", line_width=2, fillcolor="rgba(0,0,0,0)"),
        width=640, height=640, margin=dict(l=40, r=40, t=60, b=40),
    )
    # Row 0 at the top, and square pixels — see COORDINATE CONVENTION above.
    fig.update_yaxes(autorange="reversed", scaleanchor="x", scaleratio=1)
    fig._config = {"modeBarButtonsToAdd": ["drawrect", "drawcircle",
                                           "drawclosedpath", "eraseshape"]}
    return fig


# ------------------------------------------------------- shapes -> ImageJ ---
def _rect_points(x0, y0, x1, y1):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=np.float32)


def _ellipse_points(x0, y0, x1, y1, n=64):
    """Plotly 'circle' shapes are defined by their bounding box."""
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return np.column_stack([cx + rx * np.cos(t), cy + ry * np.sin(t)]).astype(np.float32)


def _path_points(path: str):
    """Parse an SVG path from a freeform draw: 'M x,y L x,y ... Z'."""
    nums = re.findall(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?", path)
    pts = np.array(nums, dtype=np.float32).reshape(-1, 2)
    return pts


def shapes_to_rois(fig, names=None, *, frame_shape=None):
    """
    Convert the shapes drawn on `fig` into a list of `roifile.ImagejRoi`.

    Parameters
    ----------
    fig : the FigureWidget returned by make_drawer()
    names : list of str, optional
        Names in draw order. Missing entries fall back to roi_1, roi_2, ...
        Name them meaningfully — the name becomes the CSV filename downstream,
        and for a transmission measurement you want matched pairs
        (e.g. "sample" / "openbeam").
    frame_shape : (H, W), optional
        If given, coordinates are clamped into the frame and a warning is
        printed for any shape that had to be clipped.
    """
    shapes = list(getattr(fig.layout, "shapes", ()) or ())
    if not shapes:
        raise ValueError(
            "No shapes on the figure. Draw at least one region first — pick "
            "'Draw rectangle' in the toolbar at the top right, then drag."
        )

    names = list(names or [])
    rois = []
    for i, sh in enumerate(shapes):
        kind = getattr(sh, "type", None)
        if kind == "rect":
            pts = _rect_points(sh.x0, sh.y0, sh.x1, sh.y1)
        elif kind == "circle":
            pts = _ellipse_points(sh.x0, sh.y0, sh.x1, sh.y1)
        elif kind == "path":
            pts = _path_points(sh.path)
        else:
            print(f"  skipping unsupported shape type {kind!r}")
            continue

        if frame_shape is not None:
            H, W = frame_shape
            clipped = np.clip(pts, [0, 0], [W - 1, H - 1])
            if not np.allclose(clipped, pts):
                print(f"  WARNING shape {i}: drawn partly outside the "
                      f"{H}x{W} frame; clamped to the edge.")
            pts = clipped

        name = names[i] if i < len(names) else f"roi_{i + 1}"
        roi = roifile.ImagejRoi.frompoints(pts)

        # *** REQUIRED, AND EASY TO MISS ***
        # frompoints() defaults to roitype 7 (FREEHAND). save_roi's
        # get_roi_mask() only rasterizes types 0-3 (polygon/rect/oval/line)
        # and 10 (point); anything else falls through to a fallback that
        # returns an ALL-ZERO MASK — silently, with no error and no warning.
        # POLYGON (0) is rasterized by the same point-in-polygon path for
        # rectangles, ellipses and freeform alike, so force it here.
        roi.roitype = roifile.ROI_TYPE.POLYGON

        roi.name = name
        rois.append(roi)

    print(f"{len(rois)} ROI(s): {[r.name for r in rois]}")
    return rois


def save_rois(path, rois):
    """Write ImageJ ROIs to a .zip that save_roi (and ImageJ) can read."""
    path = Path(path)
    if path.exists():
        path.unlink()          # roiwrite appends; stale entries would survive
    roifile.roiwrite(str(path), rois)
    print(f"wrote {len(rois)} ROI(s) -> {path}")
    return path


# ------------------------------------------------------------ sanity check ---
def check_rois(roi_path, frame_shape) -> pd.DataFrame:
    """
    Report how much of each ROI actually lands on the frame.

    An ImageJ .roi stores coordinates in the pixel frame of the image it was
    DRAWN on. `get_roi_mask` silently clips anything outside your stack and
    only warns when a mask ends up completely empty — so a ROI that is 99%
    off-frame passes quietly and hands you a spectrum from a sliver.

    Run this after every ROI file you make or receive.
    """
    from save_roi.core import load_imagej_rois, get_roi_mask

    H, W = frame_shape[-2:]
    rows = []
    for r in load_imagej_rois(str(roi_path)):
        o = r["roi_object"]
        m = get_roi_mask(o, (H, W))
        bbox = (o.bottom - o.top) * (o.right - o.left)

        # Clipping is decided by the ROI's BOUNDS vs the frame, not by an
        # area ratio. An area test would flag every non-rectangular ROI:
        # an ellipse fills only pi/4 ~ 79% of its bounding box even when it
        # sits entirely on the frame.
        overhang = max(0, -o.top) + max(0, -o.left) + \
                   max(0, o.bottom - H) + max(0, o.right - W)

        if m.sum() == 0:
            status = "FULLY OFF-FRAME"
        elif overhang:
            status = f"CLIPPED (bounds {o.top}:{o.bottom}, {o.left}:{o.right})"
        else:
            status = "ok"

        rows.append(dict(name=r["name"], bbox=bbox, mask_px=int(m.sum()),
                         fill=m.sum() / bbox if bbox else 0.0, status=status))

    df = pd.DataFrame(rows)
    bad = df[df.status != "ok"]
    print(f"frame {H}x{W}   (fill = mask/bbox; ~79% is normal for an ellipse)")
    print(df.to_string(index=False,
                       formatters={"fill": lambda v: f"{v:.0%}"}))
    if len(bad):
        print("\nDO NOT USE:", ", ".join(bad.name))
    return df


# ------------------------------------------------------------ grid preview ---
def grid_preview(radio: np.ndarray, grid_size: int = 8, *, pixel_pitch_um=55.0,
                 zmax_percentile: float = 99.5):
    """
    Overlay the grid tiling on the radiograph — i.e. show your MAP RESOLUTION
    before committing to an extraction run.

    Grid mode is the SOW deliverable path: every tile becomes one CSV, one
    independent Bragg-edge fit, and one pixel of the final parameter map.
    `grid_size` IS the resolution, and the statistics/resolution trade is
    fixed the moment you choose it — relative error goes as 1/sqrt(N), so
    doubling grid_size quarters your error bar and quarters your map's
    linear resolution.
    """
    import plotly.graph_objects as go

    H, W = radio.shape
    ny, nx = int(np.ceil(H / grid_size)), int(np.ceil(W / grid_size))
    zmax = float(np.percentile(radio, zmax_percentile)) or float(radio.max())

    fig = go.Figure(go.Heatmap(z=radio, colorscale="gray", zmin=0, zmax=zmax,
                               showscale=False))
    for k in range(1, nx):
        fig.add_vline(x=k * grid_size - 0.5, line=dict(color="cyan", width=0.5))
    for k in range(1, ny):
        fig.add_hline(y=k * grid_size - 0.5, line=dict(color="cyan", width=0.5))

    pitch = grid_size * pixel_pitch_um
    fig.update_layout(
        title=(f"grid_size={grid_size} → {nx}×{ny} = {nx*ny} cells "
               f"({nx*ny} fits) · {pitch:.0f} µm per map pixel"),
        width=640, height=640, margin=dict(l=40, r=40, t=60, b=40))
    fig.update_yaxes(autorange="reversed", scaleanchor="x", scaleratio=1)

    counts_per_cell = radio.sum() / (nx * ny)
    print(f"grid_size={grid_size}: {nx}x{ny} = {nx*ny} cells, "
          f"{pitch:.0f} um per map pixel")
    print(f"  mean counts per cell (all TOF bins): {counts_per_cell:,.0f}"
          f"  -> ~{100/np.sqrt(max(counts_per_cell,1)):.1f}% relative error "
          f"if spread over one bin")
    print("  Remember: run the SAME grid_size on the open beam too, or "
          "from_counts has nothing to divide by.")
    return fig
