import numpy as np


def matrices_from_zvec(z_vec):
    """
    generate a set of rotation matrices M such that M @ [0, 0, 1] = vec for each vec in z_vec
    https://gist.github.com/alisterburt/1722347a5de4fb469d3cb3b02eb8e5cc
    """
    basis_z = np.repeat([[0, 0, 1]], len(z_vec), axis=0)

    # cross product to find axis about which rotation should occur
    axis = np.cross(basis_z, z_vec, axis=1)
    # dot product equals cosine of angle between normalised vectors
    cos_angle = np.einsum('ij, ij -> i', basis_z, z_vec)
    # k is a constant which appears as a factor in the rotation matrix
    k = 1 / (1 + cos_angle)

    # construct rotation matrix
    r = np.empty((len(z_vec), 3, 3))
    r[:, 0, 0] = (axis[:, 0] * axis[:, 0] * k) + cos_angle
    r[:, 0, 1] = (axis[:, 1] * axis[:, 0] * k) - axis[:, 2]
    r[:, 0, 2] = (axis[:, 2] * axis[:, 0] * k) + axis[:, 1]
    r[:, 1, 0] = (axis[:, 0] * axis[:, 1] * k) + axis[:, 2]
    r[:, 1, 1] = (axis[:, 1] * axis[:, 1] * k) + cos_angle
    r[:, 1, 2] = (axis[:, 2] * axis[:, 1] * k) - axis[:, 0]
    r[:, 2, 0] = (axis[:, 0] * axis[:, 2] * k) - axis[:, 1]
    r[:, 2, 1] = (axis[:, 1] * axis[:, 2] * k) + axis[:, 0]
    r[:, 2, 2] = (axis[:, 2] * axis[:, 2] * k) + cos_angle

    return r


def generate_matrices(starts, ends, rotations):
    """
    generate rotation matrices from start and end points (defining z direction)
    and a rotation value in degrees (around z). Initialization of rotation is arbitrary.
    """
    z_vec = ends - starts
    z_vec = z_vec / np.linalg.norm(z_vec, axis=1).reshape(-1, 1)

    # initialize matrices
    mat = matrices_from_zvec(z_vec)

    # rotate them based on provided rotation
    rotations = np.array(rotations) * 2 * np.pi / 360
    rot_z = np.tile(np.eye(3), (len(z_vec), 1, 1))
    rot_z[:, 0, 0] = np.cos(rotations)
    rot_z[:, 0, 1] = -np.sin(rotations)
    rot_z[:, 1, 0] = np.sin(rotations)
    rot_z[:, 1, 1] = np.cos(rotations)

    mat = np.einsum('nij, njk -> nik', mat, rot_z)
    return mat


def matrices_to_vectors(starts, matrices):
    """
    for each matrix and position generate an x, y and z vector in napari style
    """
    xyz = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    vectors = np.einsum('nij, mj -> nmi', matrices, xyz).reshape(-1, 3)
    starts = np.repeat(starts, 3, axis=0)
    return np.stack([starts, vectors], axis=1)
