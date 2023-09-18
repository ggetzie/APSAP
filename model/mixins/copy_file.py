from plyfile import PlyData, PlyProperty


from pathlib import Path



class CopyFileMixin:


    def fixAndCopyPly(self, source, target):

        if source == target or Path(source) == Path(target):
            print("Source cannot be the same as target")
            return
        #Read the pointcloud
        plydata = PlyData.read(source)

        #go through all property one by one and if it is a double, we change it to an equivalent property in float
        real_properties = []
        for i in plydata.elements[0].properties:
            if str(PlyProperty(i.name, "double")) == str(i):
                real_properties.append(PlyProperty(i.name, "float32"))
            else:
                real_properties.append(i)


        real_properties = tuple(real_properties)
        #Save the same ply file but with float properties instead of doubl
        plydata.elements[0].properties = real_properties
        #Write the data back to the original pointcloud
        plydata.write(target)