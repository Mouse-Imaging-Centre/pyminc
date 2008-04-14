import re

# given that these methods will always be called as bound instances of
# a class a throwaway instance (or self) first argument is needed
def spawn(instance, argstring):
    """runs the command through a system call"""
    print argstring

def sgeExec(argstring):
    """runs the command using the Sun Grid Engine batch queuing system"""
    pass

class pipelineInput:
    """any input that can be processed by a pipeline

    A pipeline input has three possible states:
    1) waiting - the input does not yet exist in a form ready to be
       used.
    2) processing - the input is currently being operated on.
    3) ready - the input is ready to be used by another process.
    """
    def __init__(self):
        self.status = "unknown"
    def setProcessing(self):
        self.status = "processing"
    def setReady(self):
        self.status = "ready"
    def setWaiting(self):
        self.status = "waiting"
    def isReady(self):
        """returns True when input is ready to be used"""
        return self.status == "ready"

class filenameInput(pipelineInput):
    """a pipeline input corresponding to an on-disk file"""
    def __init__(self, filename):
        pipelineInput.__init__(self)
        self.filename = filename
        
class pipelineExecutable:
    """a command to be run through a pipeline"""
    execMethod = spawn
    def __init__(self, argstring, input=None, output=None):
        self.status = "unknown"
        self.unformattedArgs = argstring
        self.input = input
        self.output = output
        #self.execMethod = pipelineExecutable.execMethod

        # get everything ready for execution
        #self.configureInputs()
        self.formatArgstring()
    def isRunnable(self):
        """returns true if all dependencies have been satisfied"""
        unsatisfied = [x for x in self.inputs if x.status is not "ready"]
        if unsatisfied:
            return False
        else:
            return True
    def run(self):
        """execute the command using the static execMethod"""
        self.execMethod(self.formattedArgs)
    def configureInputs(self):
        """set status of all inputs and outputs"""
        for o in self.output:
            o.setWaiting()
    def formatArgstring(self):
        """parse the argstring"""
        # argstring looks something like 'command input[0] input[1] output[0]'
        # or 'command inputs outputs'
        self.formattedArgs = self.unformattedArgs
        # regular expressions to match inputs and outputs
        inputExpression = re.compile(r'input\[\d+\]')
        outputExpression = re.compile(r'output\[\d+\]')
        # find all possible matches
        inputMatches = inputExpression.findall(self.unformattedArgs)
        outputMatches = outputExpression.findall(self.unformattedArgs)
        # evaluate the matches
        inputs = [eval(x, vars(self)) for x in inputMatches]
        outputs = [eval(x, vars(self)) for x in outputMatches]
        # substitute the matches
        for i in range(len(inputMatches)):
            self.formattedArgs = self.formattedArgs.replace(inputMatches[i], 
                                                            inputs[i])
        for i in range(len(outputMatches)):
            self.formattedArgs = self.formattedArgs.replace(outputMatches[i],
                                                            outputs[i])
        # match the plural case
        self.formattedArgs = self.formattedArgs.replace("inputs",
                                                        " ".join(self.input))
        self.formattedArgs = self.formattedArgs.replace("outputs",
                                                        " ".join(self.output))

class Pipeline:
    def __init__(self, basedir=None):
        self.basedir = basedir
        self.directories = {}
        self.items = {}
        self.steps = {}
    def addDirectory(self, name, path=None):
        """add a directory to pipeline"""
        #if directory exists, throw exception
        if test.has_key(name):
            raise "exception" # should be replaced by a real exception
        #if path was given take full path
        if path:
            self.directories[name] = "/".join([path, name])
        else:
            self.directories[name] = "/".join([self.basedir, name])
    def addItem(self, name, filename, directory=None):
        """adds an item (such as a filename) to the pipeline"""
        if test.has_key(name):
            raise "exception" # should be replaced by a real exception
        if directory:
            self.items[name] = "/".join([directory, filename])
        else:
            self.items[name] = filename

if __name__ == "__main__":
    test = pipelineExecutable("command input[0] input[1] output[0]",
                              input=["test1.mnc", "test2.mnc"],
                              output=["out1.mnc"])
    test.run()
    test = pipelineExecutable("command input[1] inputs output[0]",
                              input=["test1.mnc", "test2.mnc"],
                              output=["out1.mnc"])
    test.run()
