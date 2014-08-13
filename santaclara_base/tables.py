class Cell(object):
    def __init__(self,txt):
        self.txt=txt
        self.th=False
        self.rowspan=1
        self.colspan=1

    def __unicode__(self): 
        return self.txt

    def __nonzero__(self): return True

class EmptyCell(Cell):
    def __init__(self): 
        Cell.__init__(self,"")

    def __nonzero__(self): return False

class ObjectCell(Cell):
    def __init__(self,obj): 
        Cell.__init__(self,unicode(obj))
        self.obj=obj

    def __nonzero__(self): return bool(self.obj)

class Table(list):
    def __init__(self,num_rows,num_cols):
        self.num_rows=num_rows
        self.num_cols=num_cols

        list.__init__(self)
        for r in range(0,self.num_rows):
            self.append([])
            for c in range(0,self.num_cols):
                self[r].append(Cell(""))
        
