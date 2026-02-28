import os
import ast
import shutil
import pandas as pd
import csv

class ModifyLibraryFile:
    def __init__(self, FilePath):
        self.FilePath = FilePath
        self.OriginalCodeTemporaryPath = self.FilePath[:-3]+"_Original.py"
        self.OutputFilePath = self.FilePath[:-3]+"_Output.py"
        
        self.VariableDF = pd.DataFrame()
        
        # if not os.path.exists("VariableValues/"):
        #     os.makedirs("VariableValues")
        # if not os.path.exists("TraceOutput/"):
        #     os.makedirs("TraceOutput")
    
    
    def init_decorator(self):
        self.NewFile.write("import pandas as pd\n")
        self.NewFile.write("import numpy\n\n")

        self.NewFile.write("def _add_taint(variable, name):\n")
        self.NewFile.write("    def get_user_input():\n")
        self.NewFile.write("        return input("")\n")
        self.NewFile.write("    if isinstance(variable, int) or isinstance(variable, numpy.int64):\n")
        self.NewFile.write("        variable += int(get_user_input())\n")
        self.NewFile.write("    elif isinstance(variable, float) or isinstance(variable, numpy.float64):\n")
        self.NewFile.write("        variable += float(get_user_input())\n")
        self.NewFile.write("    elif isinstance(variable, complex):\n")
        self.NewFile.write("        real_part = float(get_user_input())\n")
        self.NewFile.write("        imag_part = float(get_user_input())\n")
        self.NewFile.write("        variable += complex(real_part, imag_part)\n")
        self.NewFile.write("    elif isinstance(variable, str):\n")
        self.NewFile.write("        variable += get_user_input()\n")
        self.NewFile.write("    elif isinstance(variable, list):\n")
        self.NewFile.write("        item = get_user_input()\n")
        self.NewFile.write("        variable.append(item)\n")
        self.NewFile.write("    elif isinstance(variable, tuple):\n")
        self.NewFile.write("        item = get_user_input()\n")
        self.NewFile.write("        variable = tuple(list(variable) + [item])\n")
        self.NewFile.write("    elif isinstance(variable, dict):\n")
        self.NewFile.write("        key = get_user_input()\n")
        self.NewFile.write("        value = get_user_input()\n")
        self.NewFile.write("        variable[key] = value\n")
        self.NewFile.write("    elif isinstance(variable, set):\n")
        self.NewFile.write("        item = get_user_input()\n")
        self.NewFile.write("        variable.add(item)\n")
        self.NewFile.write("    elif isinstance(variable, bytes):\n")
        self.NewFile.write("        new_bytes = bytes(get_user_input(), 'utf-8')\n")
        self.NewFile.write("        variable += new_bytes\n")
        self.NewFile.write("    elif isinstance(variable, bytearray):\n")
        self.NewFile.write("        new_bytes = bytearray(get_user_input(), 'utf-8')\n")
        self.NewFile.write("        variable += new_bytes\n")
        self.NewFile.write("    elif isinstance(variable, bool) or isinstance(variable, numpy.bool_):\n")
        self.NewFile.write("        new_bool = bool(get_user_input())\n")
        self.NewFile.write("        variable = variable or new_bool\n")
        self.NewFile.write("    elif isinstance(variable, pd.DataFrame):\n")
        self.NewFile.write("        new_data = eval(get_user_input())\n")
        self.NewFile.write("        variable = variable.append(new_data, ignore_index=True)\n")
        self.NewFile.write("    elif isinstance(variable, numpy.ndarray):\n")
        self.NewFile.write("        element = eval(get_user_input())\n")
        self.NewFile.write("        variable = numpy.append(variable, element)\n")
        # self.NewFile.write("    elif isinstance(variable, inspect.BoundArguments):\n")
        # self.NewFile.write("        variable.arguments['added_info'] = get_user_input()\n")
        self.NewFile.write("    return variable\n")     

    def reset(self):
        os.remove(self.FilePath)
        os.rename(self.OriginalCodeTemporaryPath, self.FilePath)
        os.system('rm -rf VariableValues/*')
           
    
    def add_taint(self, spaces, functionName, variableName, lineCount):
        self.NewFile.write(f"{spaces}{variableName} = _add_taint({variableName}, \'{variableName}\', {lineCount})#Taint\n")

    def GetVariableNamesAndLineNumber(self):
        var_dict = {'LineNumber': [], 'VariableName': [], 'StartLineNumber': [], 'RHS_String': []}
        # function_name = None
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                rhs_string = ast.unparse(node.value)
                if "random" not in rhs_string.lower():
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_dict['LineNumber'].append(node.end_lineno)
                        var_dict['VariableName'].append(target.id)
                        var_dict['StartLineNumber'].append(node.lineno)
                        var_dict['RHS_String'].append(rhs_string)
                        
                    elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                        if target.value.id == 'self':
                            s = f'self.{target.attr}'
                        else:
                            s = f'{target.value.id}.{target.attr}'
                        var_dict['LineNumber'].append(node.end_lineno)
                        var_dict['VariableName'].append(s)
                        var_dict['StartLineNumber'].append(node.lineno)
                        var_dict['RHS_String'].append(rhs_string)
                    elif isinstance(target, ast.Subscript):
                        # e[:, it % convergence_iter] = E
                        if isinstance(target.value, ast.Name):
                            var_dict['LineNumber'].append(node.end_lineno)
                            var_dict['VariableName'].append(target.value.id)
                            var_dict['StartLineNumber'].append(node.lineno)
                            var_dict['RHS_String'].append(rhs_string)
                        # S.flat[:: (n_samples + 1)] = preference
                        elif isinstance(target.value.value, ast.Name):
                            var_dict['LineNumber'].append(node.end_lineno)
                            var_dict['VariableName'].append(target.value.value.id)
                            var_dict['StartLineNumber'].append(node.lineno)
                            var_dict['RHS_String'].append(rhs_string)
                    # a, b = 5, 7
                    else:
                        try:
                            variable_names = [target.id for target in node.targets[0].elts if isinstance(target, ast.Name)]
                            for v in variable_names:
                                var_dict['LineNumber'].append(node.end_lineno)
                                var_dict['VariableName'].append(v)
                                var_dict['StartLineNumber'].append(node.lineno)
                                var_dict['RHS_String'].append(rhs_string)
                        except Exception as e:
                            # print("Error in ", node.lineno, self.FilePath, "\nError:", e)
                            pass
            elif isinstance(node, ast.AugAssign):
                rhs_string = ast.unparse(node.value)
                if "random" not in rhs_string.lower():
                    continue
                if isinstance(node.target, ast.Name):
                    var_dict['LineNumber'].append(node.end_lineno)
                    var_dict['VariableName'].append(node.target.id)
                    var_dict['StartLineNumber'].append(node.lineno)
                    var_dict['RHS_String'].append(rhs_string)
            
            
        self.VariableDF = pd.DataFrame(var_dict)
        # print(self.VariableDF)
        
    def CreateNewFileWithDecorator(self):
        self.GetVariableNamesAndLineNumber()
        if self.VariableDF.shape[0] == 0:
            print("No variables found in the file.")
            self.NewFile.write(self.code)
            return
        RandomVars = self.VariableDF.loc[
            self.VariableDF["RHS_String"].str.contains("random", case=False, na=False),
            ["LineNumber", "VariableName", "StartLineNumber", "RHS_String"]
        ]
        # print("RandomVars: ", RandomVars)
        if RandomVars.shape[0] == 0:
            self.NewFile.write(self.code)
            return
        
        self.init_decorator()
        '''Read Source File'''
        OrginalFile = open(self.OriginalCodeTemporaryPath, 'r')
        OrginalFileLines = OrginalFile.readlines()
        OFLines = iter(OrginalFileLines)
        lineCount = 0
        spaces = ''
        for line in OFLines:
            self.NewFile.write(line)
            lineCount+=1
            if RandomVars[RandomVars["StartLineNumber"] == lineCount].shape[0] > 0:
                num_spaces = len(line) - len(line.lstrip(' '))
                spaces = ' ' * num_spaces
            filtered_df = RandomVars[RandomVars["LineNumber"] == lineCount]
            # print("LineCount: ", lineCount, filtered_df.shape[0])
            if filtered_df.shape[0] > 0:
                # print(filtered_df)
                # num_spaces = len(line) - len(line.lstrip(' '))
                # # print("Line: ", line, len(line), "-LS-", len(line.lstrip(' ')), "Spaces - ", num_spaces)
                # spaces = ' ' * num_spaces
                for index, row in filtered_df.iterrows():
                    self.add_taint(spaces, "Global", row["VariableName"], row["LineNumber"])
                spaces = ''

                
    
    def fit(self):
        ''' Save Original Source Code '''
        if os.path.exists(self.OriginalCodeTemporaryPath) == 0:
            shutil.copy(self.FilePath, self.OriginalCodeTemporaryPath)
            
        '''Read File And Create Tree'''
        with open(self.FilePath, 'r') as file:
            self.code = file.read()
        try:
            self.tree = ast.parse(self.code)
        except SyntaxError as e:
            # os.remove(self.OriginalCodeTemporaryPath)
            print(f"Syntax error in file {self.FilePath}: {e}")
            return
        
        self.NewFile = open(self.OutputFilePath, 'w')
        
        self.CreateNewFileWithDecorator()
        
        os.remove(self.FilePath)
        os.rename(self.OutputFilePath, self.FilePath)
        os.remove(self.OriginalCodeTemporaryPath)
        # # Store LOC
        # loc = sum(1 for line in self.code.splitlines() if line.strip())
        # with open("/Users/muyeedahmed/Desktop/Gitcode/Trace_ND_Source/TraceND/LOC/loc.csv", mode='a', newline='') as csv_file:
        #     writer = csv.writer(csv_file)
            
        #     if csv_file.tell() == 0:
        #         writer.writerow(['FilePath', 'LOC'])
            
        #     writer.writerow([self.FilePath, loc])
        

        
        
        