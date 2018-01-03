from bs_helpers import utils, globals
import os


def validate_schedule_and_profit(fn, method):
    result_filenames = [globals.scheduleFilename, globals.profitFilename]
    all_filenames = result_filenames + [globals.skipfilePath]

    def append_to_invalid_lst():
        with open('invalids.txt', 'a') as fp:
            fp.write(fn + ';' + method + '\n')

    if (not os.path.isfile(globals.scheduleFilename)) or (not os.path.isfile(globals.profitFilename)):
        print('Unable to find schedule or profit file for method ' + method + '!')
        utils.batch_del(all_filenames)
    else:
        utils.syscall('java -jar ScheduleValidator.jar ' + globals.outPath + ' ' + fn)
        if os.path.isfile(globals.skipfilePath):
            utils.batch_del(all_filenames)
            append_to_invalid_lst()
        # raise Exception('Invalid schedule or profit for method ' + method + '!')
        else:
            utils.batch_del(result_filenames)
            print('Valid solution from ' + method + ' for ' + fn)
