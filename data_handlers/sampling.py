import numpy as np
'''
Code from https://github.com/rmsouza01/CD-Deep-Cascade-MR-Reconstruction/blob/master/Modules/sampling.py
Souza, Roberto et al. Dual-domain Cascade of U-nets for Multi-channel Magnetic Resonance Image Reconstruction. arXiv preprint arXiv:1911.01458, 2019. 
'''

def uniform1d(pattern_shape, factor,direction = "column"):
    """
    Description: creates a 1D uniform sampling pattern either in the row or column direction
    of a 2D image
    :param direction: sampling direction, 'row' or 'column'
    :param pattern_shape: shape of the desired sampling pattern.
    :param factor: sampling factor in the desired direction
    :return: sampling pattern image. It is a boolean image
    """

    if direction != "column":
        pattern_shape = (pattern_shape[1],pattern_shape[0])

    factor = int(factor * pattern_shape[1])

    # Generating uniformly distributed indexes
    indexes = np.random.choice(np.arange(pattern_shape[1], dtype=int), factor, replace=False)

    under_pattern = np.zeros(pattern_shape, dtype=bool)
    under_pattern[:, indexes] = True

    if direction != "column":
        under_pattern = under_pattern.T

    return under_pattern


def uniform2d(pattern_shape, factor):
    """
    Description: creates a 2D uniform sampling pattern
    :param pattern_shape: shape of the desired sampling pattern.
    :param factor: sampling factor.
    :return: sampling pattern image. It is a boolean image
    """

    N = pattern_shape[0] * pattern_shape[1]  # Image length

    factor = int(N * factor)

    # Generating uniformly distributed indexes
    indexes = np.random.choice(np.arange(N, dtype=int), factor, replace=False)
    indexes_x = indexes // pattern_shape[1]
    indexes_y = indexes % pattern_shape[1]

    under_pattern = np.zeros(pattern_shape, dtype=bool)
    under_pattern[indexes_x, indexes_y] = True
    return under_pattern

def centered_circle(image_shape,radius):
    """
    Description: creates a boolean centered circle image with a pre-defined radius
    :param image_shape: shape of the desired image
    :param radius: radius of the desired circle
    :return: circle image. It is a boolean image
    """

    center_x = image_shape[0] // 2
    center_y = image_shape[1] // 2
    
    X,Y = np.indices(image_shape)
    circle_image = ((X-center_x)**2+(Y-center_y)**2) < radius**2  # type: bool

    return circle_image


def centered_lines(image_shape, nlines,direction = "column"):
    """
    Description: creates a boolean image with centered lines.
    :param image_shape: shape of the desired image
    :param nlines: number o lines to draw
    :param direction: sampling direction, 'row' or 'column'
    :return: lines image. It is a boolean image
    """

    if direction != "column":
        image_shape = (image_shape[1],image_shape[0])

    if isinstance(nlines, float):
        nlines = int(nlines * image_shape[1])

    center = (image_shape[1] - nlines)//2
    line_image = np.zeros(image_shape, dtype=bool)
    line_image[:, center:(center+nlines)] = True

    if direction != "column":
        line_image = line_image.T

    return line_image


def uniform_pattern(pattern_shape,factor,center = True, dim="1D",radius_nlines = 5,direction = "column"):
    """
    Description: creates a uniformly distributed sampling pattern.
    :param pattern_shape: shape of the desired sampling pattern.
    :param factor: sampling factor.
    :param center: boolean variable telling whether or not sample low frequencies
    :param dim:  '1D' or '2D' sampling pattern
    :param radius_nlines: variable telling number of lines (1D) or radius (2D) to be sampled in the centre.
    :param direction: sampling direction, 'row' or 'column'. Only valid for 1D sampling
    :return: sampling pattern. It is a boolean image
    """

    if center == False:
        if dim == "1D":
            return uniform1d(pattern_shape,factor,direction)
        elif dim == "2D":
            return uniform2d(pattern_shape,factor)
        else:
            raise("Invalid option")
    else:
        if dim == "1D":
            if direction != "column":
                aux = pattern_shape[0]
            else:
                aux = pattern_shape[1]
            factor = factor - radius_nlines/aux
            factor = factor*(1+ 1.2*factor*radius_nlines/aux)
            pattern1 = uniform1d(pattern_shape,factor,direction)
            pattern2 = centered_lines(pattern_shape,radius_nlines,direction)
            return np.logical_or(pattern1,pattern2)
        elif dim == "2D":
            factor = factor - np.pi*radius_nlines*2 / (2 * pattern_shape[1]*pattern_shape[0])
            factor = factor*(1+1.2*np.pi*radius_nlines*2 / (pattern_shape[1]*pattern_shape[0]))
            pattern1 = uniform2d(pattern_shape, factor)
            pattern2 = centered_circle(pattern_shape, radius_nlines)
            return np.logical_or(pattern1, pattern2)
        else:
            raise("Invalid option")


def gaussian1d(pattern_shape, factor,direction = "column",center=None, cov=None):
    """
    Description: creates a 1D gaussian sampling pattern either in the row or column direction
    of a 2D image
    :param factor: sampling factor in the desired direction
    :param direction: sampling direction, 'row' or 'column'
    :param pattern_shape: shape of the desired sampling pattern.
    :param center: coordinates of the center of the Gaussian distribution
    :param cov: covariance matrix of the distribution
    :return: sampling pattern image. It is a boolean image
    """

    if direction != "column":
        pattern_shape = (pattern_shape[1],pattern_shape[0])

    if center is None:
        center = np.array([1.0 * pattern_shape[1] / 2 - 0.5])

    if cov is None:
        cov = np.array([[(1.0 * pattern_shape[1] / 4) ** 2]])


    factor = int(factor * pattern_shape[1])

    samples = np.array([0])

    m = 1  # Multiplier. We have to increase this value
    # until the number of points (disregarding repeated points)
    # is equal to factor

    while (samples.shape[0] < factor):

        samples = np.random.multivariate_normal(center, cov, m * factor)
        samples = np.rint(samples).astype(int)
        indexes = np.logical_and(samples >= 0, samples < pattern_shape[1])
        samples = samples[indexes]
        samples = np.unique(samples)
        if samples.shape[0] < factor:
            m *= 2
            continue

    indexes = np.arange(samples.shape[0], dtype=int)
    np.random.shuffle(indexes)
    samples = samples[indexes][:factor]

    under_pattern = np.zeros(pattern_shape, dtype=bool)
    under_pattern[:, samples] = True

    if direction != "column":
        under_pattern = under_pattern.T

    return under_pattern

def gaussian2d(pattern_shape, factor, center=None, cov=None):
    """
    Description: creates a 2D gaussian sampling pattern of a 2D image
    :param factor: sampling factor in the desired direction
    :param pattern_shape: shape of the desired sampling pattern.
    :param center: coordinates of the center of the Gaussian distribution
    :param cov: covariance matrix of the distribution
    :return: sampling pattern image. It is a boolean image
    """

    N = pattern_shape[0] * pattern_shape[1]  # Image length

    factor = int(N * factor)

    if center is None:
        center = np.array([1.0 * pattern_shape[0] / 2 - 0.5, \
                           1.0 * pattern_shape[1] / 2 - 0.5])

    if cov is None:
        cov = np.array([[(1.0 * pattern_shape[0] / 4) ** 2, 0], \
                        [0, (1.0 * pattern_shape[1] / 4) ** 2]])

    samples = np.array([0])

    m = 1  # Multiplier. We have to increase this value
    # until the number of points (disregarding repeated points)
    # is equal to factor

    while (samples.shape[0] < factor):

        samples = np.random.multivariate_normal(center, cov, m * factor)
        samples = np.rint(samples).astype(int)
        indexesx = np.logical_and(samples[:, 0] >= 0, samples[:, 0] < pattern_shape[0])
        indexesy = np.logical_and(samples[:, 1] >= 0, samples[:, 1] < pattern_shape[1])
        indexes = np.logical_and(indexesx, indexesy)
        samples = samples[indexes]
        # samples[:,0] = np.clip(samples[:,0],0,input_shape[0]-1)
        # samples[:,1] = np.clip(samples[:,1],0,input_shape[1]-1)
        samples = np.unique(samples[:, 0] + 1j * samples[:, 1])
        samples = np.column_stack((samples.real, samples.imag)).astype(int)
        if samples.shape[0] < factor:
            m *= 2
            continue

    indexes = np.arange(samples.shape[0], dtype=int)
    np.random.shuffle(indexes)
    samples = samples[indexes][:factor]

    under_pattern = np.zeros(pattern_shape, dtype=bool)
    under_pattern[samples[:, 0], samples[:, 1]] = True
    return under_pattern


def gaussian_pattern(pattern_shape,factor, dim="1D",direction = "column",center=None, cov=None):
    """
    Description: creates a Gaussian distributed sampling pattern.
    :param pattern_shape: shape of the desired sampling pattern.
    :param factor: sampling factor.
    :param dim:  '1D' or '2D' sampling pattern
    :param direction: sampling direction, 'row' or 'column'. Only valid for 1D sampling
    :param center: coordinates of the center of the Gaussian distribution
    :param cov: covariance matrix of the distribution
    :return: sampling pattern. It is a boolean image
    """

    if dim == "1D":
        return gaussian1d(pattern_shape,factor,direction,center,cov)
    elif dim == "2D":
        return gaussian2d(pattern_shape,factor,center,cov)
    else:
        raise("Invalid option")

def gaussian2d(input_shape, factor, center=None, cov=None):
    """
    :param input_shape: tuple with the shape of the 2D image
    :param factor: sampling factor.
    :param center: coordinates of the center of the Gaussian distribution
    :param cov: covariance matrix of the distribution
    :return: sampling pattern. It is a boolean image
    """

    N = input_shape[0] * input_shape[1]  # Image length

    if isinstance(factor, float):
        factor = int(N * factor)

    if center is None:
        center = np.array([1.0 * input_shape[0] / 2 - 0.5, \
                           1.0 * input_shape[1] / 2 - 0.5])

    if cov is None:
        cov = np.array([[(1.0 * input_shape[0] / 4) ** 2, 0], \
                        [0, (1.0 * input_shape[1] / 4) ** 2]])

    samples = np.array([0])

    m = 1  # Multiplier. We have to increase this value
    # until the number of points (disregarding repeated points)
    # is equal to factor

    while (samples.shape[0] < factor):

        samples = np.random.multivariate_normal(center, cov, m * factor)
        samples = np.rint(samples).astype(int)
        indexesx = np.logical_and(samples[:, 0] >= 0, samples[:, 0] < input_shape[0])
        indexesy = np.logical_and(samples[:, 1] >= 0, samples[:, 1] < input_shape[1])
        indexes = np.logical_and(indexesx, indexesy)
        samples = samples[indexes]
        # samples[:,0] = np.clip(samples[:,0],0,input_shape[0]-1)
        # samples[:,1] = np.clip(samples[:,1],0,input_shape[1]-1)
        samples = np.unique(samples[:, 0] + 1j * samples[:, 1])
        samples = np.column_stack((samples.real, samples.imag)).astype(int)
        if samples.shape[0] < factor:
            m *= 2
            continue

    indexes = np.arange(samples.shape[0], dtype=int)
    np.random.shuffle(indexes)
    samples = samples[indexes][:factor]

    under_pattern = np.zeros(input_shape, dtype=bool)
    under_pattern[samples[:, 0], samples[:, 1]] = True
    return under_pattern


def poisson_disc2d(pattern_shape, k, r):
    """
        Implementation of the Poisson disc sampling available at:
	https://scipython.com/blog/poisson-disc-sampling-in-python/
	"""

    pattern_shape = (pattern_shape[0]-1,pattern_shape[1]-1)

    center = np.array([1.0 * pattern_shape[0] / 2 + 0.5, \
                       1.0 * pattern_shape[1] / 2 + 0.5])
    width, height = pattern_shape
    # Cell side length
    a = r / np.sqrt(2)
    # Number of cells in the x- and y-directions of the grid
    nx, ny = int(width / a) + 1, int(height / a) + 1

    # A list of coordinates in the grid of cells
    coords_list = [(ix, iy) for ix in range(nx) for iy in range(ny)]
    # Initilalize the dictionary of cells: each key is a cell's coordinates, the
    # corresponding value is the index of that cell's point's coordinates in the
    # samples list (or None if the cell is empty).
    cells = {coords: None for coords in coords_list}

    def get_cell_coords(pt):
        """Get the coordinates of the cell that pt = (x,y) falls in."""
        return int(pt[0] // a), int(pt[1] // a)

    def get_neighbours(coords):
        """
		Return the indexes of points in cells neighbouring cell at coords.
		For the cell at coords = (x,y), return the indexes of points in
		the cells with neighbouring coordinates illustrated below: ie
		those cells that could contain points closer than r.

                                     ooo
                                    ooooo
                                    ooXoo
                                    ooooo
                                     ooo

		"""

        dxdy = [(-1, -2), (0, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1),
                (-2, 0), (-1, 0), (1, 0), (2, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1),
                (-1, 2), (0, 2), (1, 2), (0, 0)]

        neighbours = []
        for dx, dy in dxdy:
            neighbour_coords = coords[0] + dx, coords[1] + dy
            if not (0 <= neighbour_coords[0] < nx and
                    0 <= neighbour_coords[1] < ny):
                # We're off the grid: no neighbours here.
                continue
            neighbour_cell = cells[neighbour_coords]
            if neighbour_cell is not None:
                # This cell is occupied: store this index of the contained point.
                neighbours.append(neighbour_cell)
        return neighbours

    def point_valid(pt):
        """
		Is pt a valid point to emit as a sample?
        It must be no closer than r from any other point:
        check the cells in its immediate neighbourhood.
		"""

        cell_coords = get_cell_coords(pt)
        for idx in get_neighbours(cell_coords):
            nearby_pt = samples[idx]
            # Squared distance between or candidate point, pt, and this nearby_pt.
            distance2 = (nearby_pt[0] - pt[0]) ** 2 + (nearby_pt[1] - pt[1]) ** 2
            if distance2 < r ** 2:
                # The points are too close, so pt is not a candidate.
                return False

        # All points tested: if we're here, pt is valid
        return True

    def get_point(k, refpt):
        """
        	Try to find a candidate point relative to refpt to emit in the sample.
		We draw up to k points from the annulus of inner radius r, outer
		radius 2r around the reference point, refpt. If none of
		them are suitable (because they're too close to existing points in
		the sample), return False. Otherwise, return the pt.
		"""
        i = 0
        while i < k:
            rho, theta = np.random.uniform(r, 2 * r), np.random.uniform(0, 2 * np.pi)
            pt = refpt[0] + rho * np.cos(theta), refpt[1] + rho * np.sin(theta)
            if not (0 < pt[0] < width and 0 < pt[1] < height):
                # This point falls outside the domain, so try again.
                continue
            if point_valid(pt):
                return pt
            i += 1
        # We failed to find a suitable point in the vicinity of refpt.
        return False

    # Pick a random point to start with.
    pt = (np.random.uniform(0, width), np.random.uniform(0, height))
    samples = [pt]
    # Our first sample is indexed at 0 in the samples list...
    cells[get_cell_coords(pt)] = 0
    # ... and it is active, in the sense that we're going to look for more points
    # in its neighbourhood.
    active = [0]

    nsamples = 1
    # As long as there are points in the active list, keep trying to find samples.
    while active:
        # choose a random "reference" point from the active list.
        idx = np.random.choice(active)
        refpt = samples[idx]
        # Try to pick a new point relative to the reference point.
        pt = get_point(k, refpt)
        if pt:
            # Point pt is valid: add it to the samples list and mark it as active
            samples.append(pt)
            nsamples += 1
            active.append(len(samples) - 1)
            cells[get_cell_coords(pt)] = len(samples) - 1
        else:
            # We had to give up looking for valid points near refpt, so remove it
            # from the list of "active" points.
            active.remove(idx)
    samples = np.rint(np.array(samples)).astype(int)
    samples = np.unique(samples[:, 0] + 1j * samples[:, 1])
    samples = np.column_stack((samples.real, samples.imag)).astype(int)
    poisson_pattern = np.zeros((pattern_shape[0] + 1, \
                                pattern_shape[1] + 1), dtype=bool)
    poisson_pattern[samples[:, 0], samples[:, 1]] = True
    return poisson_pattern

def poisson_disc_pattern(pattern_shape,center = True,radius = 5, k  = 5, r = 2):
    """
    Description: creates a uniformly distributed sampling pattern.
    :param pattern_shape: shape of the desired sampling pattern.
    :param center: boolean variable telling whether or not sample low frequencies
    :param radius: variable telling radius (2D) to be sampled in the centre.
    :param k: Number of points around each reference point as candidates for a new
    sample point
    :param r: Minimum distance between samples.
    :return: sampling pattern. It is a boolean image
    """

    if center == False:
        return poisson_disc2d(pattern_shape,k,r)
    else:
        pattern1 = poisson_disc2d(pattern_shape,k,r)
        pattern2 = centered_circle(pattern_shape, radius)
        return np.logical_or(pattern1, pattern2)
