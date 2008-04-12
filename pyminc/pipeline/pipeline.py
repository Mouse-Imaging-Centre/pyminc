import re

def spawn(argstring):
    """runs the command through a system call"""
    print argstring

def sgeExec(argstring):
    """runs the command using the Sun Grid Engine batch queuing system"""
    pass

class pipelineInput:
    """any input that can be processed by a pipeline"""
    def __init__(self):
        self.status = "unknown"

class filenameInput(pipelineInput):
    """a pipeline input corresponding to an on-disk file"""
    def __init__(self):
        pipelineInput.__init__(self)
        self.filename = False
        
class pipelineExecutable:
    """a command to be run through a pipeline"""
    execMethod = spawn
    def __init__(self, argstring, input=None, output=None):
        self.status = "unknown"
        self.unformattedArgs = argstring
        self.input = input
        self.output = output
        
        # get everything ready for execution
        self.formatFilenames()
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
        apply(self.execMethod, self.formattedArgs)
    def formatFilenames(self):
        """stub method that can be overridden by subclasses"""
        pass
    def formatArgstring(self):
        """parse the argstring"""
        # argstring looks something like 'command input[0] input[1] output[0]'
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
            self.formattedArgs = self.formattedArgs.replace(inputMatches[i], inputs[i])
        for i in range(len(outputMatches)):
            self.formattedArgs = self.formattedArgs.replace(outputMatches[i], outputs[i])
        