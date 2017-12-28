from __future__ import print_function

from urllib.error import URLError
import getopt
import logging
import os
import sys
import time

from argumentParser import ArgumentParser
from argumentParser import HelpCalledException
from argumentParser import MissingArgumentException
from converter import ConversionModeException
from converter import Converter


def printHelp():
    """
    Hilfe ausgeben
    """
    print("python main.py -i <inputfile> -o <outputfile>" +
          " --dateformat \"%Y-%m-%d\" --separators english")
    print("\n")
    print("There are two modes in which the converter can be used:")
    print("\t1.\tInput XML and Output xlsx: " +
          "This means converting from any BMEcat format to ")
    print("\t--dateformat <dateformat>")
    print("\t\te.g. '%Y-%m-%d' or '%d.%m.%Y' or anything else with Y as Year" +
          ", d as day and m as month ")
    print("\t--separators <english|german|detect>")
    print("\t\te.g. -separators german leads to numbers" +
          " beeing expected like 10.000,00")
    print("\t\t     -separators english leads to numbers" +
          " beeing expected like 10,000.00")
    print("\t\t     -separators detect tries to detect" +
          " what could be there (unsafe).")
    print("Optionally:")
    print("\t--merchant <Merchantname>")
    print("\t--manufacturer <Manufacturername>")
    print("\ti.e. python main.py -i makita_bmecat.xml" +
          " -o makita_excelfilname.xlsx -merchant \"Contorion\"" +
          " -manufacturer \"Makita\"")


def findNextFreeLogfilename(logfilename):
    for i in range(1, 11):
        freeLogfilename = "{0}_{1:02n}".format(logfilename, i)
        if not os.path.exists(freeLogfilename):
            return freeLogfilename


def createFileLoggingHandler(logfilename, logLevel=logging.DEBUG,
                             logFormat='%(levelname)7s: %(message)s'):
    '''
    setUp Logging for File
    '''
    if os.path.exists(logfilename):
        try:
            os.remove(logfilename)
        except Exception:
            logfilename = findNextFreeLogfilename(logfilename)

    logfilename += ".log"
    ''' log File'''
    logFileHandler = logging.FileHandler(filename=logfilename, mode='w')
    logFileFormatter = logging.Formatter(logFormat)
    logFileHandler.setFormatter(logFileFormatter)
    logFileHandler.setLevel(logLevel)
    return logFileHandler


def configureStdoutLogging(logLevel=logging.DEBUG):
    '''
    setUp Logging for Console
    '''
    frmStdOut = logging.Formatter('%(levelname)7s - %(message)s')
    ''' Console out '''
    stdOutHandler = logging.StreamHandler(sys.stdout)
    stdOutHandler.setFormatter(frmStdOut)
    stdOutHandler.setLevel(logLevel)
    return stdOutHandler


def setUpLogging():
    loggingLevel = logging.INFO
    '''
    setUp Logging for File and Console
    '''
    logger = logging.getLogger()

    if logger.hasHandlers():
        for handler in logger.handlers:
            logger.removeHandler(handler)
            handler.flush()
            handler.close()

    # Debug Log File
    fmt = '%(levelname)7s - [%(filename)20s:%(lineno)s - %(funcName)20s()]: %(message)s'
    debugLogFileHandler = createFileLoggingHandler(
                                        logfilename="convert_debug",
                                        logFormat=fmt)
    logger.addHandler(debugLogFileHandler)

    ''' Common Log File for Validation etc.'''
    logFileHandler = createFileLoggingHandler(logfilename="convert",
                                              logLevel=logging.WARNING)
    logger.addHandler(logFileHandler)

    stdOutHandler = configureStdoutLogging()
    logger.addHandler(stdOutHandler)
    logger.setLevel(loggingLevel)


def printHelpAndExit(message=None, exitCode=None):
    if message is not None:
        logging.info(message)
    printHelp()
    if exitCode is not None:
        sys.exit(exitCode)


def main(argv):
    # Loging einstgellen: zwei Outputdateien plus Konsole
    setUpLogging()

    logging.debug('Number of arguments:', len(argv), 'arguments.')
    logging.debug('Argument List:', str(argv))

    t1 = time.clock()

    try:
        argumentParser = ArgumentParser()
        argumentParser.parse(argv)
        converter = Converter(argumentParser.getConfig())
        converter.convert()
    except HelpCalledException:
        printHelpAndExit()
    except (FileNotFoundError, URLError) as fnfe:
        printHelpAndExit("Dateiname konnte nicht gefunden werden: {0}".format(str(fnfe)), 5)
    except ConversionModeException as cme:
        printHelpAndExit("Wrong Conversion Mode: {0}".format(str(cme)), 2)
    except MissingArgumentException as mae:
        printHelpAndExit("Missing Arguments: {0}".format(str(mae)), 3)
    except getopt.GetoptError as goe:
        printHelpAndExit("Options Error: {0}".format(str(goe)), 4)
    except Exception as e:
        logging.exception("General Exception: {0}".format(str(e)))
        sys.exit(6)

    computeDuration(t1, time.clock())


def computeDuration(t1, t2):
    duration = t2 - t1
    if duration < 60:
        print('Duration in seconds: ', (t2 - t1))
    else:
        print('Duration in minutes: ', (t2 - t1) / 60)


if __name__ == '__main__':
    main(sys.argv[1:])
