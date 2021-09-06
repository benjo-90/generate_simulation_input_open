import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np


def normalize_image(nifti_image, background_mask):
    label_stat = sitk.LabelStatisticsImageFilter()
    label_stat.Execute(nifti_image, background_mask)
    mean = label_stat.GetMean(1)
    # print('normalized to ', mean)
    normalized_image = nifti_image/mean
    normalized_image.CopyInformation(nifti_image)
    return normalized_image


def matrix_from_axis_angle(a):
    # This function is from https://github.com/rock-learning/pytransform3d/
    # blob/7589e083a50597a75b12d745ebacaa7cc056cfbd/pytransform3d/rotations.py#L302
    """ Compute rotation matrix from axis-angle.
    This is called exponential map or Rodrigues' formula.
    Parameters
    ----------
    a : array-like, shape (4,)
        Axis of rotation and rotation angle: (x, y, z, angle)
    Returns
    -------
    r : array-like, shape (3, 3)
        Rotation matrix
    """
    ux, uy, uz, theta = a
    c = np.cos(theta)
    s = np.sin(theta)
    ci = 1.0 - c
    r = np.array([[ci * ux * ux + c,
                   ci * ux * uy - uz * s,
                   ci * ux * uz + uy * s],
                  [ci * uy * ux + uz * s,
                   ci * uy * uy + c,
                   ci * uy * uz - ux * s],
                  [ci * uz * ux - uy * s,
                   ci * uz * uy + ux * s,
                   ci * uz * uz + c],
                  ])

    # This is equivalent to
    # R = (np.eye(3) * np.cos(theta) +
    #      (1.0 - np.cos(theta)) * a[:3, np.newaxis].dot(a[np.newaxis, :3]) +
    #      cross_product_matrix(a[:3]) * np.sin(theta))

    return r


def resample(image, transform):
    """
    This function resamples (updates) an image using a specified transform
    :param image: The sitk image we are trying to transform
    :param transform: An sitk transform (ex. resizing, rotation, etc.
    :return: The transformed sitk image
    """
    reference_image = image
    # interpolator = sitk.sitkLinear
    interpolator = sitk.sitkLabelGaussian
    default_value = 0
    return sitk.Resample(image, reference_image, transform,
                         interpolator, default_value)


def get_center(img):
    """
    This function returns the physical center point of a 3d sitk image
    :param img: The sitk image we are trying to find the center of
    :return: The physical center point of the image
    """
    width, height, depth = img.GetSize()
    return img.TransformIndexToPhysicalPoint((int(np.ceil(width/2)),
                                              int(np.ceil(height/2)),
                                              int(np.ceil(depth/2))))


def rotation3d_z(image, theta_z, show=False):
    """
    This function rotates an image across each of the x, y, z axes by theta_x, theta_y, and theta_z degrees
    respectively
    :param image: An sitk MRI image
    # :param theta_x: The amount of degrees the user wants the image rotated around the x axis
    # :param theta_y: The amount of degrees the user wants the image rotated around the y axis
    :param theta_z: The amount of degrees the user wants the image rotated around the z axis
    :param show: Boolean, whether or not the user wants to see the result of the rotation
    :return: The rotated image
    """
    theta_z = np.deg2rad(theta_z)
    euler_transform = sitk.Euler3DTransform()
    # print(euler_transform.GetMatrix())
    image_center = get_center(image)
    euler_transform.SetCenter(image_center)

    direction = image.GetDirection()
    axis_angle = (direction[2], direction[5], direction[8], theta_z)
    np_rot_mat = matrix_from_axis_angle(axis_angle)

    # to get clockwise rotation
    # np_rot_mat = np_rot_mat * np.array([[1, -1, -1], [-1, 1, -1], [-1, -1, 1]])

    euler_transform.SetMatrix(np_rot_mat.flatten().tolist())
    resampled_image = resample(image, euler_transform)
    if show:
        slice_num = int(input("Enter the index of the slice you would like to see"))
        plt.imshow(sitk.GetArrayFromImage(resampled_image)[slice_num])
        plt.show()
    return resampled_image


def rotation3d_pmod(image, rotation_matrix, show=False):
    """
    This function rotates an image clockwise with the help of a rotation matrix
    :param image: An sitk MRI image
    :param rotation_matrix: 3x3 rotation matrix
    :param show: Boolean, whether or not the user wants to see the result of the rotation
    :return: The rotated image
    """

    euler_transform = sitk.Euler3DTransform()
    image_center = get_center(image)
    euler_transform.SetCenter(image_center)
    np_rot_mat = rotation_matrix
    euler_transform.SetMatrix(np_rot_mat.flatten().tolist())
    # print("Alte Winkel:")
    # print(np.rad2deg(euler_transform.GetAngleX()))
    # print(np.rad2deg(euler_transform.GetAngleY()))
    # print(np.rad2deg(euler_transform.GetAngleZ()))
    euler_transform.SetRotation(-euler_transform.GetAngleX(), euler_transform.GetAngleY(), -euler_transform.GetAngleZ())
    resampled_image = resample(image, euler_transform)
    if show:
        print("Winkel pmod in grad:")
        print("Um x-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleX()), 3)))
        print("Um y-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleY()), 3)))
        print("Um z-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleZ()), 3)))
    return resampled_image


def translation3d_xy(image, offset_x, offset_y, voxel_size=2.0350):
    translation_transform = sitk.TranslationTransform(3, (offset_x * voxel_size, offset_y * voxel_size, 0))
    interpolator = sitk.sitkLabelGaussian
    return sitk.Resample(image, image, translation_transform, interpolator)


def translation3d(image, offset, voxel_size_xy=2.0350, voxel_size_z=2.425):
    translation_transform = sitk.TranslationTransform(
        3, (offset[0], offset[1], offset[2])
    )
    # interpolator = sitk.sitkLabelGaussian
    interpolator = sitk.sitkLinear
    return sitk.Resample(image, image, translation_transform, interpolator)


def affine_transformation_pmod(image, transformation_dict, show=False, interpolation="LabelGaussian"):
    transformation_matrix = transformation_dict["Reslicing"]
    rotation_matrix_4d = np.copy(transformation_matrix)
    rotation_matrix_4d[0:3, 3] = 0
    translation = np.dot(transformation_matrix, np.linalg.inv(rotation_matrix_4d))[0:3, 3]

    if show:
        print("Delta X:")
        print(np.round(translation[0], 3))
        print("Delta Y:")
        print(np.round(translation[1], 3))
        print("Delta Z:")
        print(np.round(translation[2], 3))
    rotated_image = rotation3d_pmod(image, rotation_matrix_4d[0:3, 0:3], show=show)

    translation_transform = sitk.TranslationTransform(
        3, (translation[0], -translation[1], translation[2])
    )

    if interpolation == "Linear":
        interpolator = sitk.sitkLinear

    else:
        interpolator = sitk.sitkLabelGaussian

    return sitk.Resample(rotated_image, rotated_image, translation_transform, interpolator)


def get_affine_transformation_parameters_pmod(transformation_dict, show=False):
    transformation_matrix = transformation_dict["Reslicing"]
    rotation_matrix_4d = np.copy(transformation_matrix)
    rotation_matrix_4d[0:3, 3] = 0
    translation = np.dot(transformation_matrix, np.linalg.inv(rotation_matrix_4d))[0:3, 3]

    euler_transform = sitk.Euler3DTransform()
    np_rot_mat = rotation_matrix_4d[0:3, 0:3]
    euler_transform.SetMatrix(np_rot_mat.flatten().tolist())

    if show:
        print("Delta X:")
        print(np.round(translation[0], 3))
        print("Delta Y:")
        print(np.round(translation[1], 3))
        print("Delta Z:")
        print(np.round(translation[2], 3))

        print("Winkel pmod in grad:")
        print("Um x-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleX()), 3)))
        print("Um y-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleY()), 3)))
        print("Um z-Axchse:", str(np.round(-1*np.rad2deg(euler_transform.GetAngleZ()), 3)))






