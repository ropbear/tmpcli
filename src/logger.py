#!/usr/bin/env python3
import time, os, sys
from pathlib import Path
from datetime import datetime as dtg


class Logger:
    """
    Provide an easy-to-use format for logging capabilities.
    
    Logged to `./logs/<epoch_time>.log` as plaintext, newline separated

    Types {
        INFO: any general information the user should be aware of
        STAT: status of a specific process
        WARN: non critical errors that allow for continued execution
        ERRO: critical errors that halt execution
        DEBUG: messages to assist with debugging
    }

    Verbosity {
        0:no logging, 
        1:log to file only,
        2:log STAT, WARN, and ERRO to stdout... log all to file,
        3:log all to stdout and file,
        4:log only to stdout, but log everything (if fileoutput breaks)
    }
    """

    def __init__(self,verbosity=2,logpath=None):
        self.loglevels = ["INFO","STAT","WARN","ERRO","DEBUG"]
        self.verbosity = verbosity % 4
        self.logpath = logpath


    def file_init(self,newLogPath=None):
        """
        Creates the log file

        Input: path to log file

        Returns: None
        """

        # ensure the logpath is set
        if not self.logpath:
            self.logpath = Path("logs","{}.log".format(int(time.time())))
        elif newLogPath:
            self.logpath = newLogPath

        # double check logs dir exists
        try:
            os.mkdir(Path("logs"))
        except FileExistsError:
            pass
        except Exception as e:
            self.to_stdout("LOGGER","WARN","Failed to initialize logdir, continuing with ONLY stdout.{}".format(e))
            pass
        try:
            self.logfile = open(self.logpath,'w')
            self.logfile.write("Palebail log for run at {}\n".format(int(time.time())))
            self.logfile.close()
        except:
            self.to_stdout("LOGGER","WARN","Failed to initialize logfile, continuing with ONLY stdout.")
            pass


    def to_file(self,source,level,message):
        """
        Log message to logfile
        Input: Source of message, level of message, message itself
        Return: True if successful, otherwise false.
        """

        try:
            self.logfile = open(self.logpath,'a')
        except:
            self.to_stdout("LOGGER","WARN","No logfile, continuing with ONLY stdout.")
            self.verbosity = 4
            return False

        try:
            self.logfile.write("[{}] {} -- {} -- {}\n".format(source,dtg.now().strftime("%Y-%m-%d %H:%M:%S"),level,message))
            return True
        except FileNotFoundError:
            self.to_stdout("LOGGER","WARN","Log file no longer exists... logging will continue ONLY in stdout.")
            pass
        except:
            self.to_stdout("LOGGER","WARN","Logger experienced crit fail, proceeding on stdout")
            pass
                 
        self.logfile.close()
        self.verbosity = 4
        return False


    def to_stdout(self,source,level,message):
        """
        Log message to STDOUT
        Input: source and level of message, as well as the message itself
        Return: None
        """
        
        print("[{}] {} -- {} -- {}".format(source,dtg.now().strftime("%Y-%m-%d %H:%M:%S"),level,message))


    def log(self,source,level,message):
        """
        Provide top-level logic for logging
        Input: Source and level of message, as well as the message itself
        Return: None
        """

        if level not in self.loglevels:
            level = "INFO"

        # Verb 0
        if self.verbosity == 0:
            pass

        # Verb 1
        elif self.verbosity == 1:
            if not self.to_file(source,level,message):
                # log to file fails, verbosity now at 4
                self.log(source,level,message)
        # Verb 2
        elif self.verbosity == 2:
            if not self.to_file(source,level,message):
                # log to file fails, verbosity now at 4
                self.log(source,level,message)
            elif level in ["STAT","WARN","ERRO"]:
                self.to_stdout(source,level,message)
        
        # Verb 3
        elif self.verbosity == 3:
            if not self.to_file(source,level,message):
                # log to file fails, verbosity now at 4
                self.log(source,level,message)
            self.to_stdout(source,level,message)

        # Verb 4
        elif self.verbosity == 4:
            self.to_stdout(source,level,message)
        
        # Verb Unknown
        else:
            self.to_stdout("LOGGER","WARN","Invalid verbosity level, defaulting to 2")
            self.verbosity = 2
            self.log(source,level,message)

        if level == "ERRO":
            sys.exit(1)

    def cleanup(self):
        """        
        Perform cleanup for logger
        Input: None
        Return: None
        """
        if self.verbosity in [1,2,3]: #log levels which include writing to file
            try:
                self.logfile.close()
            except:
                self.to_stdout("LOGGER","WARN","Unable to close logfile")

