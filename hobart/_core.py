# Adapted from
# https://github.com/lace/lace/blob/a19d14eeca37a66af442c5a73c3934987d2d7d9a/lace/intersection.py
# https://github.com/lace/lace/blob/a19d14eeca37a66af442c5a73c3934987d2d7d9a/lace/test_intersection.py
# By Body Labs & Metabolize, BSD License

import numpy as np
from polliwog import Polyline
from scipy.spatial import cKDTree
import vg
from ._internal import EdgeMap, Graph
from ._validation import check_indices

__all__ = ["faces_intersecting_plane", "intersect_mesh_with_plane"]


def faces_intersecting_plane(vertices, faces, plane):
    """
    Efficiently compute which of the given faces intersect the given plane.

    Args:
        vertices (np.ndarray): The vertices, as a `nx3` array.
        faces (np.ndarray): The face indices, as a `kx3` array.
        plane (polliwog.Plane): The plane of interest.

    Returns:
        np.ndarray: A boolean mask indicating the faces which intersect
            the given plane.

    See also:
        https://polliwog.readthedocs.io/en/latest/#polliwog.Plane
    """
    vg.shape.check(locals(), "vertices", (-1, 3))
    vg.shape.check(locals(), "faces", (-1, 3))
    check_indices(faces, len(vertices), "faces")

    signed_distances = plane.signed_distance(vertices)
    return np.abs(np.sign(signed_distances)[faces].sum(axis=1)) != 3


def intersect_mesh_with_plane(
    vertices, faces, plane, neighborhood=None, ret_pointcloud=False
):
    """
    Takes a cross section of planar point cloud with a Mesh object.
    Ignore those points which intersect at a vertex - the probability of
    this event is small, and accounting for it complicates the algorithm.

    When a plane may intersect the mesh more than once, provide a
    `neighborhood`, which is a set of points. The cross section closest
    to this list of points is returned (using a kd-tree).

    Args:
        vertices (np.ndarray): The vertices, as a `nx3` array.
        faces (np.ndarray): The face indices, as a `kx3` array.
        plane (polliwog.Plane): The plane of interest.
        neighborhood (np.ndarray): One or more points of interest, used to
            select the desired cross section when a plane may intersect more
            than once.
        ret_pointcloud (bool): When `True`, return an unstructured point
            cloud instead of a list of polylines. This is useful when
            you aren't specifying a neighborhood and you only care about
            e.g. some apex of the intersection.

    Returns:
        list: A list of `polliwog.Polyline` instances.

    See also:
        https://polliwog.readthedocs.io/en/latest/#polliwog.Plane
        https://polliwog.readthedocs.io/en/latest/#polliwog.Polyline
    """
    if neighborhood is not None:
        vg.shape.check(locals(), "neighborhood", (-1, 3))

    # 1: Select those faces that intersect the plane, fs
    fs = faces[faces_intersecting_plane(vertices, faces, plane)]

    if len(fs) == 0:
        # Nothing intersects.
        if ret_pointcloud:
            return np.zeros((0, 3))
        elif neighborhood is not None:
            return None
        else:
            return []

    # and edges of those faces
    es = np.vstack((fs[:, (0, 1)], fs[:, (1, 2)], fs[:, (2, 0)]))

    # 2: Find the edges where each of those faces actually cross the plane
    intersection_map = EdgeMap()

    pts, pt_is_valid = plane.line_segment_xsections(
        vertices[es[:, 0]], vertices[es[:, 1]]
    )
    valid_pts = pts[pt_is_valid]
    valid_es = es[pt_is_valid]
    for val, e in zip(valid_pts, valid_es):
        if not intersection_map.contains(e[0], e[1]):
            intersection_map.add(e[0], e[1], val)
    verts = np.array(intersection_map.values)

    # 3: Build the edge adjacency graph
    G = Graph(verts.shape[0])
    for f in fs:
        # Since we're dealing with a triangle that intersects the plane,
        # exactly two of the edges will intersect (note that the only other
        # sorts of "intersections" are one edge in plane or all three edges in
        # plane, which won't be picked up by mesh_intersecting_faces).
        e0 = intersection_map.index(f[0], f[1])
        e1 = intersection_map.index(f[0], f[2])
        e2 = intersection_map.index(f[1], f[2])
        if e0 is None:
            G.add_edge(e1, e2)
        elif e1 is None:
            G.add_edge(e0, e2)
        else:
            G.add_edge(e0, e1)  # pragma: no cover

    # 4: Find the paths for each component
    components = []
    components_closed = []
    while len(G) > 0:
        path = G.pop_euler_path()
        if path is None:
            raise ValueError(  # pragma: no cover
                "Mesh slice has too many odd degree edges; can't find a path along the edge"
            )
        component_verts = verts[path]

        if np.all(component_verts[0] == component_verts[-1]):
            # Because the closed polyline will make that last link:
            component_verts = np.delete(component_verts, 0, axis=0)
            components_closed.append(True)
        else:
            components_closed.append(False)
        components.append(component_verts)

    # 6 (optional - only if 'neighborhood' is provided): Use a KDTree to select
    # the component with minimal distance to 'neighborhood'.
    if neighborhood is not None and len(components) > 1:
        tree = cKDTree(neighborhood)

        # The number of components will not be large in practice, so this loop
        # won't hurt.
        means = [np.mean(tree.query(component)[0]) for component in components]
        index = np.argmin(means)
        if ret_pointcloud:
            return components[index]
        else:
            return Polyline(components[index], is_closed=components_closed[index])
    elif neighborhood is not None and len(components) == 1:
        if ret_pointcloud:  # pragma: no cover
            return components[0]  # pragma: no cover
        else:
            return Polyline(
                components[0], is_closed=components_closed[0]
            )  # pragma: no cover
    else:
        # No neighborhood provided, so return all the components, either in a
        # pointcloud or as separate polylines.
        if ret_pointcloud:
            return np.vstack(components)
        else:
            return [
                Polyline(v, is_closed=closed)
                for v, closed in zip(components, components_closed)
            ]
