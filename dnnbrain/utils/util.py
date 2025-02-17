import cv2
import numpy as np

from dnnbrain.dnn.core import Mask


def get_frame_time_info(vid_file, original_onset, interval=1, before_vid=0, after_vid=0):
    """
    Extract frames of interest from a video with their onsets and durations,
    according to the experimental design.

    Parameters:
    -----------
    vid_file[str]: video file path
    original_onset[float]: the first stimulus' time point relative to the beginning of the response
        For example, if the response begins at 14 seconds after the first stimulus, the original_onset is -14.
    interval[int]: Get one frame per 'interval' frames
    before_vid[float]: Display the first frame as a static picture for 'before_vid' seconds before video.
    after_vid[float]: Display the last frame as a static picture for 'after_vid' seconds after video.

    Returns:
    --------
    frame_nums[list]: sequence numbers of the frames of interest
    onsets[list]: onsets of the frames of interest
    durations[list]: durations of the frames of interest
    """
    assert isinstance(interval, int) and interval > 0, "Parameter 'interval' must be a positive integer!"

    # load video information
    vid_cap = cv2.VideoCapture(vid_file)
    fps = vid_cap.get(cv2.CAP_PROP_FPS)
    n_frame = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # generate sequence numbers
    frame_nums = list(range(1, n_frame+1, interval))

    # generate durations
    duration = 1 / fps * interval
    durations = [duration] * len(frame_nums)
    durations[0] = durations[0] + before_vid
    durations[-1] = durations[-1] + after_vid

    # generate onsets
    onsets = [original_onset]
    for d in durations[:-1]:
        onsets.append(onsets[-1] + d)

    return frame_nums, onsets, durations


def gen_dmask(layers=None, channels=None, dmask_file=None):
    """
    Generate DNN mask object by:
    1. combining layers and channels.
    2. loading from dmask file.

    Parameters:
    ----------
    layers[list]: layer names
    channels[list]: channel numbers
    dmask_file[str]: .dmask.csv file

    Return:
    ------
    dmask[Mask]: DNN mask
    """
    # set some assertions
    assert np.logical_xor(layers is None, dmask_file is None), \
        "Use one and only one of the 'layers' and 'dmask_file'!"
    if layers is None:
        assert channels is None, "'channels' can't be used without 'layers'!"

    dmask = Mask()
    if layers is None:
        # load from dmask file
        dmask.load(dmask_file)
    else:
        # combine layers and channels
        # contain all rows and columns for each layer
        n_layer = len(layers)
        if n_layer == 0:
            raise ValueError("'layers' can't be empty!")
        elif n_layer == 1:
            # All channels belong to the single layer
            dmask.set(layers[0], channels)
        else:
            if channels is None:
                # contain all channels for each layer
                for layer in layers:
                    dmask.set(layer)
            elif n_layer == len(channels):
                # one-to-one correspondence between layers and channels
                for layer, chn in zip(layers, channels):
                    dmask.set(layer, [chn])
            else:
                raise ValueError("'channels' must be None or a list with same length as 'layers'"
                                 " when the length of 'layers' is larger than 1.")
    return dmask
