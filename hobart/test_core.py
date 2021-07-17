from hobart import faces_intersecting_plane, intersect_mesh_with_plane
import numpy as np
from polliwog import Plane, Polyline
import vg

box_vertices = np.array(
    [
        [0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5],
        [0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5],
        [0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5, -0.5],
    ]
).T

box_faces = np.array(
    [
        [0, 1, 2],
        [3, 2, 1],
        [0, 2, 4],
        [6, 4, 2],
        [0, 4, 1],
        [5, 1, 4],
        [7, 5, 6],
        [4, 6, 5],
        [7, 6, 3],
        [2, 3, 6],
        [7, 3, 5],
        [1, 5, 3],
    ]
)

double_box_vertices = np.vstack(
    [box_vertices, np.array([2.0, 0.0, 0.0]) + box_vertices]
)
double_box_faces = np.vstack([box_faces, len(box_vertices) + box_faces])

non_intersecting_plane = Plane(np.array([0.0, 5.0, 0.0]), vg.basis.y)


def create_open_box():
    v_on_faces_to_remove = np.nonzero(box_vertices[:, 0] < 0.0)[0]
    faces_to_remove = np.all(
        np.in1d(box_faces.ravel(), v_on_faces_to_remove).reshape((-1, 3)), axis=1
    )
    return box_faces[~faces_to_remove]


open_box_faces = create_open_box()

double_open_box_faces = np.vstack([open_box_faces, len(box_vertices) + open_box_faces])


def test_intersection():
    # Verify that we're finding the correct number of faces to start with.
    assert (
        np.count_nonzero(faces_intersecting_plane(box_vertices, box_faces, Plane.xz))
        == 8
    )

    xss = intersect_mesh_with_plane(box_vertices, box_faces, Plane.xz)
    assert isinstance(xss, list)
    assert len(xss) == 1

    (xs,) = xss
    assert xs.num_v == 8
    assert xs.is_closed is True
    assert xs.total_length == 4.0
    np.testing.assert_array_equal(xs.v[:, 1], np.zeros(8))
    for a, b in zip(xs.v[0:-1, [0, 2]], xs.v[1:, [0, 2]]):
        # Each line changes only one coordinate, and is 0.5 long.
        assert np.sum(a == b) == 1
        assert np.linalg.norm(a - b) == 0.5


def test_intersection_with_ret_pointcloud():
    (xs,) = intersect_mesh_with_plane(box_vertices, box_faces, Plane.xz)
    pointcloud = intersect_mesh_with_plane(
        box_vertices, box_faces, Plane.xz, ret_pointcloud=True
    )
    assert isinstance(pointcloud, np.ndarray)
    np.testing.assert_array_equal(pointcloud, xs.v)


def test_no_intersection():
    np.testing.assert_array_equal(
        faces_intersecting_plane(box_vertices, box_faces, non_intersecting_plane),
        np.zeros(12),
    )
    xss = intersect_mesh_with_plane(box_vertices, box_faces, non_intersecting_plane)
    assert isinstance(xss, list)
    assert xss == []


# TODO: Verify that we're detecting faces that lay entirely in the plane as
# potential intersections.


def test_no_intersection_with_neighborhood():
    neighborhood = np.zeros((1, 3))
    xs = intersect_mesh_with_plane(
        box_vertices, box_faces, non_intersecting_plane, neighborhood=neighborhood
    )
    assert xs is None


def test_no_intersection_with_ret_pointcloud():
    pointcloud = intersect_mesh_with_plane(
        box_vertices, box_faces, non_intersecting_plane, ret_pointcloud=True
    )
    assert isinstance(pointcloud, np.ndarray)
    assert pointcloud.shape == (0, 3)


def test_intersection_wth_two_components():
    xss = intersect_mesh_with_plane(double_box_vertices, double_box_faces, Plane.xz)
    assert isinstance(xss, list)
    assert len(xss) == 2

    first, second = xss
    assert first.num_v == 8
    assert second.num_v == 8
    assert first.is_closed is True
    assert second.is_closed is True


def test_intersection_wth_neighborhood():
    neighborhood = np.zeros((1, 3))
    xs = intersect_mesh_with_plane(
        double_box_vertices, double_box_faces, Plane.xz, neighborhood=neighborhood
    )
    assert isinstance(xs, Polyline)
    assert len(xs) == 8
    assert xs.is_closed is True


def test_intersection_with_neighborhood_and_ret_pointcloud():
    neighborhood = np.zeros((1, 3))
    xs = intersect_mesh_with_plane(
        double_box_vertices, double_box_faces, Plane.xz, neighborhood=neighborhood
    )
    pointcloud = intersect_mesh_with_plane(
        double_box_vertices,
        double_box_faces,
        Plane.xz,
        neighborhood=neighborhood,
        ret_pointcloud=True,
    )
    assert isinstance(pointcloud, np.ndarray)
    np.testing.assert_array_equal(pointcloud, xs.v)


def test_intersection_with_non_watertight_mesh():
    xss = intersect_mesh_with_plane(box_vertices, open_box_faces, Plane.xz)

    assert isinstance(xss, list)
    assert len(xss) == 1

    (xs,) = xss
    # The removed side is not in the xsection.
    assert not np.any(np.all(xs.v == [-0.5, 0.0, 0.0]))

    assert xs.num_v == 7
    assert xs.is_closed is False

    assert xs.total_length == 3.0

    np.testing.assert_array_equal(xs.v[:, 1], np.zeros(7))
    for a, b in zip(xs.v[0:-1, [0, 2]], xs.v[1:, [0, 2]]):
        # Each line changes only one coordinate, and is 0.5 long.
        assert np.sum(a == b) == 1
        assert np.linalg.norm(a - b) == 0.5


def test_intersection_with_mulitple_non_watertight_meshes():
    xss = intersect_mesh_with_plane(
        double_box_vertices, double_open_box_faces, Plane.xz
    )

    assert isinstance(xss, list)
    assert len(xss) == 2

    first, second = xss
    assert first.num_v == 7
    assert second.num_v == 7
    assert first.is_closed is False
    assert second.is_closed is False

    # The removed side is not in either xsection.
    assert not np.any(np.all(first.v == [-0.5, 0.0, 0.0]))
    assert not np.any(np.all(second.v == [-0.5, 0.0, 0.0]))

    assert first.total_length == 3.0
    assert second.total_length == 3.0

    np.testing.assert_array_equal(first.v[:, 1], np.zeros(7))
    np.testing.assert_array_equal(second.v[:, 1], np.zeros(7))

    for xs in xss:
        for a, b in zip(xs.v[0:-1, [0, 2]], xs.v[1:, [0, 2]]):
            # Each line changes only one coordinate, and is 0.5 long.
            assert np.sum(a == b) == 1
            assert np.linalg.norm(a - b) == 0.5
