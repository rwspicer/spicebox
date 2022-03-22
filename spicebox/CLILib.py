"""
CLI Lib
-------

Simple python cli wrapper

Rawser Spicer



taken from utilitools v0.1.0 then degree day calculator

version: 1.0.0
Split from imiq-database python utilities: 2017-08-18

"""
import sys

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
    return str(x).lower() in ['true', 't', 'yes', 'y', '1']


class CLI (object):
    """ This class will act as a simple CLI utility """
    
    def __init__ (self, mandatory, optional = [], types = {}, split_char = '='):
        """This class will act as a simple CLI utility
        
        Parameters
        ----------
        mandatory: list
            list of mandatory flags for utility
        optional: list, optional
            list of optional flags for utility
        types: dict, optional
            dictioanry of each flag with the type it should be 
            
        .. note:: -h or --help are reserved to rasis help requested error
    
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
        self.args = {}
        if type(mandatory) is dict:
            self.flags = list(mandatory.keys())

            passed_flags = {}
            for item in sys.argv[1:]: #sys.argv[0] is script
                if split_char in item:
                    flag, value = item.split(split_char)
                else:
                    flag, value = item, None
                passed_flags[flag] = value

                
            missing_required = []
            used_keys = []
            for flag in mandatory.keys():
                # print(flag)
                details = mandatory[flag]

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
                del(mandatory[key])
                
    

            if len(missing_required ) != 0:
                err = ''
                for flag in missing_required :
                    err += 'Required Flag(%s) missing\n' % flag
                
                raise CLILibMandatoryError(err)
            if len(passed_flags) != 0:
                err = ''
                for flag in mandatory:
                    if '--help' in flag or '--h' in flag: ## TODO change?
                        raise CLILibHelpRequestedError

                    err += 'Flag(%s) not recognized\n' % flag
                
                raise CLILibUnknownFlagError(err)

        # else: # old style cli
        #     self.flags = mandatory + optional
        #     # print(self.flags)
            
        #     if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        #         raise CLILibHelpRequestedError
            
        #     for item in sys.argv[1:]:
        #         try:
        #             flag, value = item.split('=')
        #             self.args[flag] = value
        #         except ValueError:
        #             flag = item.split('=')[0]
        #             self.args[flag] = True


        #     for flag in mandatory:
        #         if not flag in self.args.keys():
        #             raise CLILibMandatoryError(
        #                 "Invalid mandatory flags. Missing:", flag
        #             )

        #     for flag in self.args.keys():
        #         if not flag in self.flags:
        #             raise CLILibMandatoryError(
        #                 "Invalid flags:", flag
        #             )
        #     if len(types) != 0:
        #         for flag in types:
        #             try:
        #                 self.args[flag] = types[flag]( self.args[flag] )
        #             except ValueError:
        #                 msg = 'Type of argument ' + flag + \
        #                     ' must be ' + str(types[flag]) + '.'
        #                 raise CLILibTypeError (msg)
        #             except KeyError:
        #                 pass
            
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
    # except  CLILibMandatoryError:
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
   

