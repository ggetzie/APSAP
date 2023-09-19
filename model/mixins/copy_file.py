from plyfile import PlyData, PlyProperty
from pathlib import Path


class CopyFileMixin:

    def fixAndCopyPly(self, source, target):
        """This function fixes the 3d model from the source url and put it into the target url.
        This makes sure the 3d model can be opened with Gigamesh.

        It fixes the 3d model by replacing the ply file's header's double properties with float properties.

        Args:
            source (str): The url of the source 3d model that may crash Gigamesh
            target (str): The url of the fixed 3d model
        """
        if source[-4:] != ".ply" or target[-4:] != ".ply":
            print("Source and Target must be valid ply")

        if source == target or Path(source) == Path(target):
            print("Source cannot be the same as target")
            return

        plydata = PlyData.read(source)

        real_properties = []
        for i in plydata.elements[0].properties:
            if str(PlyProperty(i.name, "double")) == str(i):
                real_properties.append(PlyProperty(i.name, "float32"))
            else:
                real_properties.append(i)
       
        real_properties = tuple(real_properties)
        plydata.elements[0].properties = real_properties

        plydata.write(target)
