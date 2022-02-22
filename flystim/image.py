from skimage import filters
from skimage.io import imread
from flystim import util
import numpy as np


class Image:
    """Image class."""

    def __init__(self, image_name):
        self.image_name = image_name
        self.image_path = util.get_resource_path(image_name)

    def load_image(self):
        """ Return the image as an array """
        return imread(self.image_path).astype(np.uint8)

    def whiten_image(self):
        """ Return a whitened version of the image."""
        raw_image = self.load_image()

        X_norm = raw_image / raw_image.max()  # Rescale to [0, 1]
        X_norm = X_norm - X_norm.mean(axis=0)  # Mean subtract
        cov = np.cov(X_norm, rowvar=False)

        U, S, V = np.linalg.svd(cov)

        epsilon = 0.1  # Don't blow up tiny noisy modes
        X_ZCA = U.dot(np.diag(1.0/np.sqrt(S + epsilon))).dot(U.T).dot(X_norm.T).T

        # Rescale back to same max pixel value
        whitened_image = raw_image.max() * (X_ZCA - X_ZCA.min()) / (X_ZCA.max() - X_ZCA.min())

        return whitened_image

    def filter_image(self, filter_name, filter_kwargs={}):
        """
        Return a filtered version of the image.

        params:
            filter_name: can be any filter name in skimage.filters
                see - https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.difference_of_gaussians
            filter_kwargs: dict of keyword args for named filter
        """
        raw_image = self.load_image()
        filter_fxn = getattr(filters, filter_name)
        filtered_img = filter_fxn(raw_image, **filter_kwargs)

        # Rescale image: approx the same mean + stdev as the raw image
        filtered_img = raw_image.std() * (filtered_img / filtered_img.std())
        filtered_img += raw_image.mean() - filtered_img.mean()

        # Clip so it lives on [0, 255]: will make the mean and stdev a bit different than the raw
        filtered_img[filtered_img < 0] = 0
        filtered_img[filtered_img > 255] = 255

        # Cast back to 8 bit
        return filtered_img.astype(np.uint8)
