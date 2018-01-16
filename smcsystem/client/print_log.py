import logging

class Log():
    def __init__(self,logname,logger,level):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(level)
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def getlog(self):
        return self.logger