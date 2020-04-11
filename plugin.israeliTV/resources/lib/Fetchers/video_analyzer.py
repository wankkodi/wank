# Numeric.
import numpy as np


class VideoAnalyzer(object):
    @staticmethod
    def compare_images(img1, img2):
        """
        Compares between the two images and return the difference index between the images.
        0 means the images are identical. The higher the difference, the more different are the images.
        :param img1: image1 (numpy matrix)
        :param img2: image2 (numpy matrix)
        :return: score of the images
        """
        if img1.shape != img2.shape:
            raise RuntimeError('The dimensions of the images are different.\n'
                               'Image 1 dimensions: {shp1}.\n'
                               'Image 2 dimensions: {shp2}.\n'.format(shp1=img1.shape, shp2=img2.shape))
        diff = np.sum(np.absolute(img1 - img2))
        return diff

    @staticmethod
    def compare_movies(mov1, mov2, num_of_probes=10):
        """
        Compares between the two movies and return the differences between the frames.
        :param mov1: movie1 (MoviePy object).
        :param mov2: movie2 (MoviePy object).
        :param num_of_probes: number of probes we take between
        :return:
        """
        # todo: to finish
        pass
