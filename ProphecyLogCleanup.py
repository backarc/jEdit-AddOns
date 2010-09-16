#!/usr/bin/python
#
###!C:\Python25\python.exe
# $RCSfile: ProphecyLogCleanup.py,v $
#
# $Author: kschmitte $
# $Date: 2010/05/04 13:28:12 $
# $Revision: 1.3 $
#
# Copyright (C) 2002-2010 Voxeo Germany GmbH. All Rights Reserved. Confidential
#
# Clean up Prophecy logs to make them readable
# from Kai Schmitte
# 04/2010


########################################################################
#Imports
#needed system libs for execution:
import getopt, sys, os, cStringIO, cgi, datetime, re
#import time


########################################################################
#the exception class
class prophecyLogCleanupException(Exception):
    """prophecyLogCleanupException
       the exception class for prophecyLogCleanup
    """
    def __init__(self, method, message):
        """__init__(self, method, message)
        set method and message to internal values
        """
        self.method = method
        self.message = message

    def __str__(self):
        """__str__(self)
        returns: "Error in " + self.method + "()! Message: " + self.message
        """
        return "Error in " + self.method + "()! Message: " + self.message




########################################################################
#the main class
class prophecyLogCleanup(object):
    '''prophecyLogCleanup
    the main class
    prophecyLogCleanup.py will take a file or a folder and clean up the layout of Prophecy logs
    to make them better readble.  
    '''

    def __init__(self, directory="", settingsFile="settings.xml"):
        """ __init__(self, directory="", settingsFile="settings.xml")
        Constructor
        Currently sets only the starting directory (or singlefile to be processed)
        settingsfFile is ignored. 
        """
        #get the settings
        #self.settings = self._getSettings(settingsFile) -> not needed in the moment
        dir = os.path.abspath(directory)
        self.rootDirectory = self._add_path_slash(dir)
        #DEBUG: print self.rootDirectory

    
    def changeFiles(self):
        """changeFiles
        actually the main method
        Converts all files if self.rootDirectory is a dir - otherwise only the given file"""
        #check if this is a file:
        if os.path.isfile(self.rootDirectory):
            self._convertFile(self.rootDirectory)
        else:
            #get the file list
            fileList = self._getDirectoryFiles()
            #walk through the files
            for fileName in fileList:
                #DEBUG: 
                print "processing " + fileName
                #convert file
                self._convertFile(fileName)
            
            
    def _convertFile(self, fileName):
        """_convertFile(self, fileName)
        changes the layout for one single file
        """
        #open file
        fileContent = self._openFile(fileName)
        #change the content
        newFileContent = self.changeLineEndChars(fileContent)
        fileContent = self.changeSlashes(newFileContent)
        fileContent = self.changeTabs(fileContent)
        #save the file back to the disk
        self._saveFile(fileName, fileContent)
 
    
    def changeLineEndChars(self,  fileContent):
        """ changeLineEndChars(self,  fileContent)
        change the "\\r\\n" to "\\n" 
        and "\\n" to "\n" (line break)
        """
        try:
            result1 = re.sub(r"(\\r)?\\n", "\n", fileContent) 
            #result1 = re.sub("\\r\\n", "\n", fileContent)
            #print result1
#            f = file("test.txt", 'w')
#            f.write(fileContent)
#            f.close()
            result = re.sub("\\n", "\n", result1)
            #print result
        except:
            raise prophecyLogCleanupException("changeLineEndChars", "Error in changing file content")
        return result
       
        
    def changeSlashes(self,  fileContent):
        """ changeSlashes(self,  fileContent)
        change the "\s" to "/"
        """
        try:
            #result = re.sub(r"\\s", "/", fileContent) 
            result = fileContent.replace("\\s",  "/")
        except:
            raise prophecyLogCleanupException("changeSlashes", "Error in changing file content")
        return result
        
        
    def changeTabs(self,  fileContent):
        """ changeTabs(self,  fileContent)
        change the "\\t" to "\t" (a tab)
        """
        try:
            result = re.sub(r"\\t", "\t", fileContent) 
        except:
            raise prophecyLogCleanupException("changeTabs", "Error in changing file content")
        return result
	
        
        
 #--- helper methods ------------------------------------------------------
    def _getDirectoryFiles(self):
        """_getDirectoryFiles
        gets all files ending with .xml from self.rootDirectoy dir
        returns a list of files
        """
        filelist = []
        allFiles = os.listdir(self.rootDirectory)
        for oneFile in allFiles:
            filePath = os.path.join(self.rootDirectory,  oneFile)
            if os.path.isfile(filePath) and oneFile[0:3] != "new":
                filelist.append(oneFile)
        return filelist
    
    
    def _searchFile(self, fileName):
        """_searchFile(self, fileName)
        Search given filename recursively in pythonpath and working directory.
        """
        #check
        pathList = filter(os.path.isdir, sys.path)
        #add the path were the script is executed from
        if os.getcwd() not in pathList:
            pathList.append(os.getcwd())
            pathList.reverse()
        #add the path were the scipt is located in
        if sys.argv[0] not in pathList:
            pathList.append(os.path.dirname(sys.argv[0]))
            pathList.reverse()
        #look for the file:
        for path in pathList:
            walker = os.walk(path)
            for dirPath, dirNames, fileNames in walker:
                if fileName in fileNames:
                    return os.path.join(dirPath, fileName)
        return ""


    def _openFile(self,  fileName):
        """_openFile(self,  fileName)
         open a file into fileContent
        """
        complFileN = os.path.join(self.rootDirectory,  fileName)
        fileContent = ""
        #check if file exists
        if not os.path.exists(complFileN):
            #except here!
            print filename + " not found"
            raise prophecyLogCleanupException("_openFile", "File could not be found. Filename: " + complFileN)

        try:
            f = file(complFileN, 'r')
            fileContent = f.read()
            f.close()
        except:
            #except here as licenseParserError
            raise prophecyLogCleanupException("_openFile", "File could not be read. Filename: " + complFileN)
        #if no error - return filecontent
        return fileContent
    
    
    def _saveFile(self,  fileName, fileContent):
        """_saveFile 
            save a file from fileContent to fileName
        """
        complFileN = os.path.join(self.rootDirectory, fileName)
        #check if file exists
        if not os.path.exists(complFileN):
            #except here!
            print filename + " not found"
            raise prophecyLogCleanupException("_saveFile", "File could not be found. Filename: " + complFileN)

        try:
            f = file(complFileN, 'w')
            f.write(fileContent)
            f.close()
        except:
            try:
                newFileName = "new_" + fileName
                f = file(os.path.join(self.rootDirectory, newFileName),  'w')            
                f.write(fileContent)
                f.close()
            except:
                raise prophecyLogCleanupException("_saveFile", "File could not be written. Filename: " + complFileN + " Failover to " + newFileName + " failed also")


    def _add_path_slash(self, s_path):
        """_add_path_slash(s_path)
        http://stackoverflow.com/questions/1855477/how-to-access-sys-argv-or-any-string-variable-in-raw-mode
        """
        if not s_path:
            return s_path
        if 2 == len(s_path) and ':' == s_path[1]:
            return s_path  # it is just a drive letter
        if s_path[-1] in ('/', '\\'):
            return s_path
        if s_path[-1] in ("\"", "\'"):
            return s_path[:len(s_path)-1] + '\\'
        return s_path + '\\'

        
        
        
#run if script is simply executed
if __name__ == "__main__":
    print  len(sys.argv)
    if  len(sys.argv) < 2:
        print "Please provide a folder to convert"
        sys.exit(2)
    #get the start path
    startPath = sys.argv[1]
#    f = file("test_kai.txt",  'w')            
#    f.write(startPath)
#    f.close()
    print "start"
#    print startPath
    #create the class
    reader = prophecyLogCleanup(startPath)
    reader.changeFiles()
    print "end"
