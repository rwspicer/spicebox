"""
CLI Lib
-------

Simple python cli wrapper

Rawser Spicer




Parts of this code once existed as parts of the imiq-database python utilities,
utilitools, and the degree day calculator. 
"""
import sys
import copy

class CLILibTypeError(Exception):
    """CLILib type error, raised if type is wrong for a provided flag
    """
    pass
    
class CLILibMandatoryError(Exception):
    """CLILib mandatory flag error, raised if all of the mandatory flags 
    are not present
    """
    pass

class CLILibUnknownFlagError(Exception):
    """CLILib mandatory flag error, raised if all of the mandatory flags 
    are not present
    """
    pass

class CLIInvalidValueError(Exception):
    """CLILib mandatory flag error, raised if all of the mandatory flags 
    are not present
    """
    pass
    
class CLILibHelpRequestedError(Exception):
    """CLILib help requested error, raised if -h or --help is provied in the 
    lsit of flags
    """
    pass


def to_bool(x):
    """ this function converts various values to a bool. Any value not in the 
    following list(case insensitive) is interpeated as false:
        'true'
        't', 
        'yes' 
        'y' 
        '1' or 1 as in int
    
    Parameters
    ----------
    x: any

    Returns 
    -------
    bool
    """
    return str(x).lower() in ['true', 't', 'yes', 'y', '1']


class CLI (object):
    """ This class will act as a simple CLI utility """
    
    def __init__ (self, config_ori,  split_char = '='):
        """This class will act as a simple CLI utility
        
        Parameters
        ----------
        mandatory: dict
            dictionary with cli flags as keys. Values are are dicts with
            the keys: 'required', 'type', 'default', and 'accepted-values'
            Only the key 'required' must be provided, and indicates if the 
            flag is required for utility to work.
            'type' should be a python type if provided
            'default' should be a default value for the flag if provided.
            'accepted-values' is a list of possible values the flag may have
            if provided. 

        split_char: str, optional, default '='
            char to split command flags and valuse at cli
        
            
        .. note:: -h or --help are reserved to raised help requested error
    
        attributes
        ----------
        flags: list
            lais of all flags for utility
        args: dict
            dictionary of each flag with its values
            
        raises
        ------
        CLILibHelpRequestedError 
            if -h or --help are provided in list of flags
        
        """
        config = copy.deepcopy(config_ori)

        self.args = {}
        self.flags = list(config.keys())

        passed_flags = {}
        for item in sys.argv[1:]: #sys.argv[0] is script
            if split_char in item:
                flag, value = item.split(split_char)
            else:
                flag, value = item, None
            passed_flags[flag] = value

            
        missing_required = []
        used_keys = []
        for flag in config.keys():
            # print(flag)
            details = config[flag]

            if details['required'] == True and not flag in passed_flags: 
                missing_required.append(flag)
                continue
            elif details['required'] == False and not flag in passed_flags:
                value = details['default'] if 'default' in details else None

            else: # not missing and not default
                value = passed_flags[flag]

            
            if 'type' in details:

                
                if details['type'] is bool: ## if bool do extra checks
                    value = to_bool(value)
                # elif: ## TODO add list support
                #     details['type'] is list:
                else: # else basic type conversion
                    # try:
                    if not value is None:
                        value = details['type'](value)
                    
                # except TypeError as E:
                    elif details['required'] == False and \
                                not (not 'default' in details \
                                and not type(value) is None):
                        raise TypeError(E)
                    # else if there is no default none values are fine
                        


                    
            if 'accepted-values' in details:
                if (not value in details['accepted-values']) and \
                        not (value is None):# and details['required'] == False and not 'default' in details):
                    msg = 'Value of: %s, not accepted for flag: %s.\n'
                    msg += 'Use one of the following insted: %s' 
                    msg = msg % (value, flag, details['accepted-values'])
                    raise CLIInvalidValueError(msg)                    

            used_keys.append(flag)
            self.args[flag] = value
            if flag in passed_flags:
                del(passed_flags[flag])

        for key in used_keys:    
            del(config[key])
            


        if len(missing_required ) != 0:
            err = ''
            for flag in missing_required :
                err += 'Required Flag(%s) missing\n' % flag
            
            raise CLILibMandatoryError(err)
        if len(passed_flags) != 0:
            # print (passed_flags)
            err = ''
            for flag in passed_flags:
                # print(flag)
                if '--help' in flag or '--h' in flag: ## TODO change?
                    raise CLILibHelpRequestedError

                err += 'Flag(%s) not recognized\n' % flag
            
            raise CLILibUnknownFlagError(err)


            
    def __repr__ (self):
        """
        """
        return str(self.args)
        
    def __getitem__ (self, key):
        """get opperator for utility, gets a flags value
        
        parameters
        ----------
        key: str
            the flag to get the value for
        
        returns
        -------
        the utilitys flags value
        """
        try:
            return self.args[key]
        except KeyError:
            if key in self.flags:
                return None
            else:
                raise KeyError(key)
        
        
        
        

if __name__ == "__main__":
    """ example utility """
    # try:
    #     test = CLI(['--a','--b'],['--c'],
    #         types = {'--a':int, '--b': float, '--c':str})
    #     print (type(test['--a']), test['--a'])
    #     print (type(test['--b']), test['--b'])
    #     print (type(test['--c']), test['--c'])
    # except  CLILibconfigError:
    #     print ("Valid flags are: --a, --b, and --c(optional)")
    # except  CLILibTypeError as E:
    #     print (E)
        
    flags = {
        '--a': {'required': True, 'type': bool},
        '--b': {'required': True, 'type': str, 'accepted-values':['t','f']},
        '--c': {'required': False, 'type': bool, 'default': True}
    }

    print('test 1')
    sys.argv = ['test.py', '--a=True', '--b=f']
    test = CLI(flags)
    print (type(test['--a']), test['--a'])
    print (type(test['--b']), test['--b'])
    print (type(test['--c']), test['--c'])

    print('test 2')
    sys.argv = ['test.py', '--a=True', '--b=F']
    flags = {
        '--a': {'required': True, 'type': bool},
        '--b': {'required': True, 'type': str, 'accepted-values':['t','f']},
        '--c': {'required': False, 'type': bool, 'default': True}
    }
    try:
        test = CLI(flags)
    except CLIInvalidValueError:
        pass
    

    print('test 3')
    sys.argv = ['test.py', '--a=True', '--b=f', '--c=1']
    flags = {
        '--a': {'required': True, 'type': bool},
        '--b': {'required': True, 'type': str, 'accepted-values':['t','f']},
        '--c': {'required': False, 'type': bool, 'default': True}
    }
    test = CLI(flags)
    print (type(test['--a']), test['--a'])
    print (type(test['--b']), test['--b'])
    print (type(test['--c']), test['--c'])

    print('test 4')
    sys.argv = ['test.py', '--b=f', '--c=1']
    flags = {
        '--a': {'required': True, 'type': bool},
        '--b': {'required': True, 'type': str, 'accepted-values':['t','f']},
        '--c': {'required': False, 'type': bool, 'default': True}
    }
    try:
        test = CLI(flags)
    except CLILibMandatoryError:
        pass
        
    print('test 5')
    sys.argv = ['test.py', '--a=True', '--b=f', '--c=1', '--d=bogus']
    flags = {
        '--a': {'required': True, 'type': bool},
        '--b': {'required': True, 'type': str, 'accepted-values':['t','f']},
        '--c': {'required': False, 'type': bool, 'default': True}
    }
    try:
        test = CLI(flags)
    except CLILibUnknownFlagError:
        pass
   

