from supsisim.qtvers import *

from supsisim.const import PW

class Port(QGraphicsPathItem):
    """A block holds ports that can be connected to."""
    def __init__(self, parent, scene, name = ''):
        super(Port, self).__init__(parent)
        self.scene = scene
        self.block = None
        self.name = ''
        self.line_color = Qt.GlobalColor.black
        self.fill_color = Qt.GlobalColor.black
        self.p = QPainterPath()
        self.connections = []
        self.nodeID = '0'
        self.parent = parent

    def setup(self):
        pass

    def itemChange(self, change, value):
#        if change == self.ItemScenePositionHasChanged:
        if change == QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges:
            for conn in self.connections:
                try:
                    conn.update_pos_from_ports()
                except AttributeError:
                    self.connections.remove(conn)
        return value

    def is_connected(self, other_port):
        for conn in self.connections:
            if conn.port1 == other_port or conn.port2 == other_port:
                return True
        return False

    def remove(self):
        for el in self.connections.copy():
            el.remove()

    def setFlip(self):
        isflipped = self.parent.flip
        if isflipped:
            self.setTransform(QTransform.fromScale(-1, 1))
        else:
            self.setTransform(QTransform.fromScale(1, 1))

class InPort(Port):
    def __init__(self, parent, scene):
        super(InPort, self).__init__(parent, scene)
        self.setup()

    def __str__(self):
        txt  = 'InPort \n'
        txt += 'Node ID :' + self.nodeID + '\n'
        txt += 'Connections: ' + (len(self.connections)).__str__() + '\n'
        return txt

    def setup(self):
        self.setPen(self.line_color)
        self.p.moveTo(-PW, -PW)
        self.p.lineTo(0.0,0.0)
        self.p.lineTo(-PW, PW)
        self.setPath(self.p)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)

class OutPort(Port):
    def __init__(self, parent, scene):
        super(OutPort, self).__init__(parent, scene)
        self.setup()

    def __str__(self):
        txt  = 'OutPort \n'
        txt += 'Node ID :' + self.nodeID + '\n'
        txt += 'Connections: ' + (len(self.connections)).__str__() + '\n'
        return txt

    def setup(self):
        self.setPen(self.line_color)
        self.setBrush(self.fill_color)
        self.p.moveTo(0.0, -PW)
        self.p.lineTo(PW,0.0)
        self.p.lineTo(0.0, PW)
        self.setPath(self.p)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
