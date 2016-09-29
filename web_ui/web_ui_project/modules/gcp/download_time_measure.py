from cloud_storage import Bucket
from waves import Waves
import timeit

class TimeMeasure:
    timeholder = []

    #1st file
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020206_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #2nd file

    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020207_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start

    #3rd
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020208_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #4th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020209_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #5th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020210_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #6th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020211_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #7th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020212_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #8th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020213_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #9th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020214_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start
    #10th
    start = timeit.default_timer()
    bk = Bucket("uk-test-download-time", "g-test-1022")
    data = bk.get("2015020215_34C731FFFE472310.gz")
    stop = timeit.default_timer()
    timeholder.append(stop - start)
    print stop - start

    with open("Time_to_download.txt", mode="w") as file_w:
        file_w.write('Time for downloading\n')
        for item in timeholder:
            file_w.write("%s\n" % item)


