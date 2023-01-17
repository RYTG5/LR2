import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate

from StdReinfShapeBuilder.RotationAngles import RotationAngles
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from HandleService import HandleService

class CreateBridge:
    def __init__(self, doc):
        self.El_list = []
        self.handle_list = []
        self.document = doc

    def create(self, buildEl):
        self._top_sh_width = buildEl.TopShWidth.value
        self._top_sh_height = buildEl.TopShHeight.value

        self._bot_sh_width = buildEl.BotShWidth.value
        self._bot_sh_up_height = buildEl.BotShUpHeight.value
        self._bot_sh_low_height = buildEl.BotShLowHeight.value
        self._bot_sh_height = self._bot_sh_up_height + self._bot_sh_low_height

        if buildEl.RibThick.value > min(self._top_sh_width, self._bot_sh_width):
            buildEl.RibThick.value = min(self._top_sh_width, self._bot_sh_width)
        self._rib_thickness = buildEl.RibThick.value
        self._rib_height = buildEl.RibHeight.value

        self._beam_length = buildEl.BeamLength.value
        self._beam_width = max(self._top_sh_width, self._bot_sh_width)
        self._beam_height = buildEl.BeamHeight.value

        self._hole_depth = buildEl.HoleDepth.value
        self._hole_height = buildEl.HoleHeight.value

        self._angleX = buildEl.RotationAngleX.value
        self._angleY = buildEl.RotationAngleY.value
        self._angleZ = buildEl.RotationAngleZ.value

        self.create_beam(buildEl)
        self.create_handles(buildEl)

        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), self._angleX, self._angleY, self._angleZ,
                                             self.El_list)

        rot_angles = RotationAngles(self._angleX, self._angleY, self._angleZ)
        HandleService.transform_handles(self.handle_list, rot_angles.get_rotation_matrix())

        return self.El_list, self.handle_list

    def create_beam(self, buildEl):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = buildEl.Color3.value
        com_prop.Stroke = 1


        bottom_shelf = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._beam_width - self._bot_sh_width) / 2., 0., 0.),
                                       AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._bot_sh_width,
            self._beam_length, self._bot_sh_height)

        edges = AllplanUtil.VecSizeTList()
        edges.append(10)
        edges.append(8)
        err, bottom_shelf = AllplanGeo.ChamferCalculus.Calculate(bottom_shelf, edges, 20., False)


        top_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0.,
                               self._beam_height - self._top_sh_height), AllplanGeo.Vector3D(1, 0, 0),
            AllplanGeo.Vector3D(0, 0, 1)), self._top_sh_width, self._beam_length, self._top_sh_height)

        top_shelf_notch = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0., self._beam_height - 45.),
            AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), 60., self._beam_length, 45.)
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        top_shelf_notch = AllplanGeo.Move(top_shelf_notch, AllplanGeo.Vector3D(self._top_sh_width - 60., 0, 0))
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return

        err, beam = AllplanGeo.MakeUnion(bottom_shelf, top_shelf)
        if not GeometryValidate.polyhedron(err):
            return


        rib = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0., 0., self._bot_sh_height), AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)), self._beam_width, self._beam_length,
            self._rib_height)

        err, beam = AllplanGeo.MakeUnion(beam, rib)
        if not GeometryValidate.polyhedron(err):
            return


        left_notch_pol = AllplanGeo.Polygon2D()
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2.,
                                             self._beam_height - self._top_sh_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2., self._bot_sh_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._bot_sh_width) / 2., self._bot_sh_low_height)
        left_notch_pol += AllplanGeo.Point2D(0., self._bot_sh_low_height)
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._top_sh_width) / 2., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2.,
                                             self._beam_height - self._top_sh_height)
        if not GeometryValidate.is_valid(left_notch_pol):
            return

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 0, 0)
        path += AllplanGeo.Point3D(0, buildEl.BeamLength.value, 0)

        err, notches = AllplanGeo.CreatePolyhedron(left_notch_pol, AllplanGeo.Point2D(0., 0.), path)
        if GeometryValidate.polyhedron(err):
            edges = AllplanUtil.VecSizeTList()
            if self._rib_thickness == self._bot_sh_width:
                edges.append(0)
            elif self._rib_thickness == self._top_sh_width:
                edges.append(1)
            else:
                edges.append(0)
                edges.append(2)
            err, notches = AllplanGeo.FilletCalculus3D.Calculate(notches, edges, 100., False)

            plane = AllplanGeo.Plane3D(AllplanGeo.Point3D(self._beam_width / 2., 0, 0), AllplanGeo.Vector3D(1, 0, 0))
            right_notch = AllplanGeo.Mirror(notches, plane)

            err, notches = AllplanGeo.MakeUnion(notches, right_notch)
            if not GeometryValidate.polyhedron(err):
                return

            err, beam = AllplanGeo.MakeSubtraction(beam, notches)
            if not GeometryValidate.polyhedron(err):
                return


        sling_holes = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(0, buildEl.HoleDepth.value, buildEl.HoleHeight.value),
                AllplanGeo.Vector3D(0, 0, 1), AllplanGeo.Vector3D(1, 0, 0)),
            45.5,
            self._beam_width
        )

        sling_hole_moved = AllplanGeo.Move(
            sling_holes, AllplanGeo.Vector3D(0., self._beam_length - self._hole_depth * 2, 0)
        )

        err, sling_holes = AllplanGeo.MakeUnion(sling_holes, sling_hole_moved)
        if not GeometryValidate.polyhedron(err):
            return

        err, beam = AllplanGeo.MakeSubtraction(beam, sling_holes)
        if not GeometryValidate.polyhedron(err):
            return


        self.El_list.append(AllplanBasisElements.ModelElement3D(com_prop, beam))
        
    def create_handle1(self):
        handle1 = HandleProperties(
            "BeamLength",
            AllplanGeo.Point3D(0., self._beam_length, 0.),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamLength", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle1)

    def create_handle2(self):
        handle2 = HandleProperties(
            "BeamHeight",
            AllplanGeo.Point3D(0., 0., self._beam_height),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamHeight", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle2)

    def create_handle3(self):
        handle3 = HandleProperties(
            "TopShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._top_sh_width) / 2. + self._top_sh_width, 0., self._beam_height - 45.
            ),
            AllplanGeo.Point3D((self._beam_width - self._top_sh_width) / 2., 0, self._beam_height - 45.),
            [("TopShWidth", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle3)
    def create_handle4(self):
        handle4 = HandleProperties(
            "BotShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._bot_sh_width) / 2. + self._bot_sh_width, 0., self._bot_sh_low_height
            ),

            AllplanGeo.Point3D((self._beam_width - self._bot_sh_width) / 2., 0, self._bot_sh_low_height),
            [("BotShWidth", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle4)

    def create_handle5(self):
        handle5 = HandleProperties(
            "RibThick",
            AllplanGeo.Point3D(
                (self._beam_width - self._rib_thickness) / 2. + self._rib_thickness, 0., self._beam_height / 2.
            ),
            AllplanGeo.Point3D((self._beam_width - self._rib_thickness) / 2., 0, self._beam_height / 2.),
            [("RibThick", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle5)

def check_allplan_version(buildEl, version):

    del buildEl
    del version

    return True


def create_element(buildEl, doc):

    element = CreateBridge(doc)


    return element.create(buildEl)


def move_handle(buildEl, handle_prop, input_pnt, doc):

    buildEl.change_property(handle_prop, input_pnt)


    check_equality(handle_prop.handle_id, buildEl)
    check_Height(buildEl)


    return create_element(buildEl, doc)

def check_equality(handle_id,buildEl):
    if handle_id == "BeamHeight":
        buildEl.RibHeight.value = buildEl.BeamHeight.value - buildEl.TopShHeight.value - \
                                buildEl.BotShLowHeight.value - buildEl.BotShUpHeight.value

def check_Height(buildEl):
    if buildEl.HoleHeight.value > buildEl.BeamHeight.value - buildEl.TopShHeight.value - 45.5:
            buildEl.HoleHeight.value = buildEl.BeamHeight.value - buildEl.TopShHeight.value - 45.5

def change_property(buildEl, name, value):

    if name == "BeamHeight":
        change = value - buildEl.TopShHeight.value - buildEl.RibHeight.value - \
                 buildEl.BotShUpHeight.value - buildEl.BotShLowHeight.value

        print(change)
        change_equality(change, buildEl,value)
    else:
        Switch(buildEl,name,value)

    return True

def change_equality(change,buildEl,value):
    if change < 0:
        change = abs(change)
        if buildEl.TopShHeight.value > 320.:
            if buildEl.TopShHeight.value - change < 320.:
                change -= buildEl.TopShHeight.value - 320.
                buildEl.TopShHeight.value = 320.
            else:
                buildEl.TopShHeight.value -= change
                change = 0.
        if (change != 0) and (buildEl.BotShUpHeight.value > 160.):
            if buildEl.BotShUpHeight.value - change < 160.:
                change -= buildEl.BotShUpHeight.value - 160.
                buildEl.BotShUpHeight.value = 160.
            else:
                buildEl.BotShUpHeight.value -= change
                change = 0.
        if (change != 0) and (buildEl.BotShLowHeight.value > 153.):
            if buildEl.BotShLowHeight.value - change < 153.:
                change -= buildEl.BotShLowHeight.value - 153.
                buildEl.BotShLowHeight.value = 153.
            else:
                buildEl.BotShLowHeight.value -= change
                change = 0.
        if (change != 0) and (buildEl.RibHeight.value > 467.):
            if buildEl.RibHeight.value - change < 467.:
                change -= buildEl.RibHeight.value - 467.
                buildEl.RibHeight.value = 467.
            else:
                buildEl.RibHeight.value -= change
                change = 0.
    else:
        buildEl.RibHeight.value += change
    if value - buildEl.TopShHeight.value - 45.5 < buildEl.HoleHeight.value:
        buildEl.HoleHeight.value = value - buildEl.TopShHeight.value - 45.5

def Switch(buildEl,name,value):
    if name == "TopShHeight":
        buildEl.BeamHeight.value = value + buildEl.RibHeight.value + \
                                     buildEl.BotShUpHeight.value + buildEl.BotShLowHeight.value
    if name == "RibHeight":
        buildEl.BeamHeight.value = value + buildEl.TopShHeight.value + \
                                     buildEl.BotShUpHeight.value + buildEl.BotShLowHeight.value
    if name == "BotShUpHeight":
        buildEl.BeamHeight.value = value + buildEl.TopShHeight.value + \
                                     buildEl.RibHeight.value + buildEl.BotShLowHeight.value
        if value + buildEl.BotShLowHeight.value + 45.5 > buildEl.HoleHeight.value:
            buildEl.HoleHeight.value = value + buildEl.BotShLowHeight.value + 45.5
    if name == "BotShLowHeight":
        buildEl.BeamHeight.value = value + buildEl.TopShHeight.value + \
                                     buildEl.RibHeight.value + buildEl.BotShUpHeight.value
        if buildEl.BotShUpHeight.value + value + 45.5 > buildEl.HoleHeight.value:
            buildEl.HoleHeight.value = buildEl.BotShUpHeight.value + value + 45.5
    if name == "HoleHeight":
        if value > buildEl.BeamHeight.value - buildEl.TopShHeight.value - 45.5:
            buildEl.HoleHeight.value = buildEl.BeamHeight.value - buildEl.TopShHeight.value - 45.5
        elif value < buildEl.BotShLowHeight.value + buildEl.BotShUpHeight.value + 45.5:
            buildEl.HoleHeight.value = buildEl.BotShLowHeight.value + buildEl.BotShUpHeight.value + 45.5
    if name == "HoleDepth":
        if value >= buildEl.BeamLength.value / 2.:
            buildEl.HoleDepth.value = buildEl.BeamLength.value / 2. - 45.5


