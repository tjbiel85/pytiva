def matching_shift_from_collection(label, collection):
    """Return matching ProviderShift object in collection, according to label"""
    label = str(label).upper()
    match = False
    for s in collection:
        comparator = str(s.label).upper()
        if comparator == label:
            if not match:
                match = s
            else:
                raise Exception(f'Found more than one match ({s} and {match})')

    return match


def earliest_starting_time(shift_collection):
    """Find the ProviderShift object in shift_collection with the earliest starting time"""
    earliest = False
    for i in range(len(shift_collection)):
        if i == 0:
            earliest = shift_collection[i].start
        else:
            comparison = shift_collection[i].start
            if comparison < earliest:
                earliest = comparison

    return earliest


def latest_ending_time(shift_collection):
    """Find the ProviderShift object in shift_collection with the latest ending time"""
    latest = False
    for i in range(len(shift_collection)):
        if i == 0:
            latest = shift_collection[i].end
        else:
            comparison = shift_collection[i].end
            if comparison > latest:
                latest = comparison

    return latest
