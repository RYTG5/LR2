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

    def create(self, build_El):   
        self.create_top(self, build_EL)
        self.create_bot(self, build_EL)
        self.create_holeAngle(self, build_EL)
        self.create_B(build_El)
        self.create_handle12(self)
        self.create_handle34(self)
        self.create_handle5(self)

        AllplanBaseElements.ElementTransform(AllplanGeo.Vector3D(), self._angleX, self._angleY, self._angleZ,
                                             self.El_list)

        rot_angles = RotationAngles(self._angleX, self._angleY, self._angleZ)
        HandleService.transform_handles(self.handle_list, rot_angles.get_rotation_matrix())

        return self.El_list, self.handle_list
    def create_top(self, build_EL):
        self._topSH_width = build_El.TopShWidth.value
        self._topSH_height = build_El.TopShHeight.value
    def create_bot(self, build_EL):
        self._botSH_width = build_El.BotShWidth.value
        self._botSH_up_height = build_El.BotShUpHeight.value
        self._botSH_low_height = build_El.BotShLowHeight.value
        self._botSH_height = self._botSH_up_height + self._botSH_low_height
        self._rib_thickness = build_El.RibThick.value
        self._rib_height = build_El.RibHeight.value
        self.RibThick_equality(self, build_El)
        self._beam_length = build_El.BeamLength.value
        self._beam_width = max(self._topSH_width, self._botSH_width)
        self._beam_height = build_El.BeamHeight.value
    def create_holeAngle(self, build_EL): 
        self._hole_depth = build_El.HoleDepth.value
        self._hole_height = build_El.HoleHeight.value
        self._angleX = build_El.RotationAngleX.value
        self._angleY = build_El.RotationAngleY.value
        self._angleZ = build_El.RotationAngleZ.value
        
    def RibThick_equality(self, build_El):
        if build_El.RibThick.value > min(self._topSH_width, self._botSH_width):
            build_El.RibThick.value = min(self._topSH_width, self._botSH_width)
    def create_B(self, build_El):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = build_El.Color3.value
        com_prop.Stroke = 1

        bottom_shelf = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D((self._beam_width - self._botSH_width) / 2., 0., 0.),
                                       AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), self._botSH_width,
            self._beam_length, self._botSH_height)

        edges = AllplanUtil.VecSizeTList()
        edges.append(10)
        edges.append(8)
        err, bottom_shelf = AllplanGeo.ChamferCalculus.Calculate(bottom_shelf, edges, 20., False)

        top_shelf = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D((self._beam_width - self._topSH_width) / 2., 0.,
                               self._beam_height - self._topSH_height), AllplanGeo.Vector3D(1, 0, 0),
            AllplanGeo.Vector3D(0, 0, 1)), self._topSH_width, self._beam_length, self._topSH_height)

        top_shelf_notch = AllplanGeo.BRep3D.CreateCuboid(AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D((self._beam_width - self._topSH_width) / 2., 0., self._beam_height - 45.),
            AllplanGeo.Vector3D(1, 0, 0), AllplanGeo.Vector3D(0, 0, 1)), 60., self._beam_length, 45.)
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return
        top_shelf_notch = AllplanGeo.Move(top_shelf_notch, AllplanGeo.Vector3D(self._topSH_width - 60., 0, 0))
        err, top_shelf = AllplanGeo.MakeSubtraction(top_shelf, top_shelf_notch)
        if not GeometryValidate.polyhedron(err):
            return

        err, beam = AllplanGeo.MakeUnion(bottom_shelf, top_shelf)
        if not GeometryValidate.polyhedron(err):
            return

        rib = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0., 0., self._botSH_height), AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)), self._beam_width, self._beam_length,
            self._rib_height)

        err, beam = AllplanGeo.MakeUnion(beam, rib)
        if not GeometryValidate.polyhedron(err):
            return

        left_notch_pol = AllplanGeo.Polygon2D()
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2.,
                                             self._beam_height - self._topSH_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2., self._botSH_height)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._botSH_width) / 2., self._botSH_low_height)
        left_notch_pol += AllplanGeo.Point2D(0., self._botSH_low_height)
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D(0., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._topSH_width) / 2., self._beam_height - 100.)
        left_notch_pol += AllplanGeo.Point2D((self._beam_width - self._rib_thickness) / 2.,
                                             self._beam_height - self._topSH_height)
        if not GeometryValidate.is_valid(left_notch_pol):
            return

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 0, 0)
        path += AllplanGeo.Point3D(0, build_El.BeamLength.value, 0)

        err, notches = AllplanGeo.CreatePolyhedron(left_notch_pol, AllplanGeo.Point2D(0., 0.), path)
        geometry_equality(self, notches, beam, err)

        sling_holes = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(
                AllplanGeo.Point3D(0, build_El.HoleDepth.value, build_El.HoleHeight.value),
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

    def create_handle12(self):
        handle1 = HandleProperties(
            "BeamLength",
            AllplanGeo.Point3D(0., self._beam_length, 0.),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamLength", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle1)

        handle2 = HandleProperties(
            "BeamHeight",
            AllplanGeo.Point3D(0., 0., self._beam_height),
            AllplanGeo.Point3D(0, 0, 0),
            [("BeamHeight", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle2)
    def create_handle34(self):
        handle3 = HandleProperties(
            "TopShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._topSH_width) / 2. + self._topSH_width, 0., self._beam_height - 45.
            ),
            AllplanGeo.Point3D((self._beam_width - self._topSH_width) / 2., 0, self._beam_height - 45.),
            [("TopShWidth", HandleDirection.point_dir)],
            HandleDirection.point_dir, True
        )
        self.handle_list.append(handle3)
        handle4 = HandleProperties(
            "BotShWidth",
            AllplanGeo.Point3D(
                (self._beam_width - self._botSH_width) / 2. + self._botSH_width, 0., self._botSH_low_height
            ),

            AllplanGeo.Point3D((self._beam_width - self._botSH_width) / 2., 0, self._botSH_low_height),
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

def geometry_equality(self,notches,beam,err) :
    if GeometryValidate.polyhedron(err):
        edges = AllplanUtil.VecSizeTList()
        if self._rib_thickness == self._botSH_width:
            edges.append(0)
        elif self._rib_thickness == self._topSH_width:
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

def allplan_version(build_El, version):
    del build_El
    del version

    return True


def create_element(build_El, doc):
    element = CreateBridge(doc)

    return element.create(build_El)


def move_handle(build_El, handle_prop, input_pnt, doc):
    build_El.change_property(handle_prop, input_pnt)

    RibHeight_equality(handle_prop.handle_id, build_El)
    HoleHeight_equality(build_El)

    return create_element(build_El, doc)


def RibHeight_equality(handle_id, build_El):
    if handle_id == "BeamHeight":
        build_El.RibHeight.value = build_El.BeamHeight.value - build_El.TopShHeight.value - \
                                  build_El.BotShLowHeight.value - build_El.BotShUpHeight.value


def HoleHeight_equality(build_El):
    if build_El.HoleHeight.value > build_El.BeamHeight.value - build_El.TopShHeight.value - 45.5:
        build_El.HoleHeight.value = build_El.BeamHeight.value - build_El.TopShHeight.value - 45.5


def change_property(build_El, name, value):
    if name == "BeamHeight":
        change = value - build_El.TopShHeight.value - build_El.RibHeight.value - \
                 build_El.BotShUpHeight.value - build_El.BotShLowHeight.value

        print(change)
        change_prop_equality(change, build_El, value)
    else:
        if name == "TopShHeight" or name == "RibHeight":
            variation(build_El, name, value)
        if name == "BotShUpHeight" or name == "BotShLowHeight":
            variation_bot_height(build_El, name, value)
        if name == "HoleHeight" or name == "HoleDepth":
            variation_hole(build_El, name, value)
    return True


def change_prop_equality(change, build_El, value):
    if change < 0:
        change = abs(change)
        if build_El.TopShHeight.value > 320.:
            if build_El.TopShHeight.value - change < 320.:
                change -= build_El.TopShHeight.value - 320.
                build_El.TopShHeight.value = 320.
            else:
                build_El.TopShHeight.value -= change
                change = 0.
        if (change != 0) and (build_El.BotShUpHeight.value > 160.):
            if build_El.BotShUpHeight.value - change < 160.:
                change -= build_El.BotShUpHeight.value - 160.
                build_El.BotShUpHeight.value = 160.
            else:
                build_El.BotShUpHeight.value -= change
                change = 0.
        if (change != 0) and (build_El.BotShLowHeight.value > 153.):
            if build_El.BotShLowHeight.value - change < 153.:
                change -= build_El.BotShLowHeight.value - 153.
                build_El.BotShLowHeight.value = 153.
            else:
                build_El.BotShLowHeight.value -= change
                change = 0.
        if (change != 0) and (build_El.RibHeight.value > 467.):
            if build_El.RibHeight.value - change < 467.:
                change -= build_El.RibHeight.value - 467.
                build_El.RibHeight.value = 467.
            else:
                build_El.RibHeight.value -= change
                change = 0.
    else:
        build_El.RibHeight.value += change
    if value - build_El.TopShHeight.value - 45.5 < build_El.HoleHeight.value:
        build_El.HoleHeight.value = value - build_El.TopShHeight.value - 45.5


def variation(build_El, name, value):
    if name == "TopShHeight":
        build_El.BeamHeight.value = value + build_El.RibHeight.value + \
                                   build_El.BotShUpHeight.value + build_El.BotShLowHeight.value
    if name == "RibHeight":
        build_El.BeamHeight.value = value + build_El.TopShHeight.value + \
                                   build_El.BotShUpHeight.value + build_El.BotShLowHeight.value
def variation_bot_height(build_El, name, value):
    if name == "BotShUpHeight":
        build_El.BeamHeight.value = value + build_El.TopShHeight.value + \
                                    build_El.RibHeight.value + build_El.BotShLowHeight.value
        if value + build_El.BotShLowHeight.value + 45.5 > build_El.HoleHeight.value:
            build_El.HoleHeight.value = value + build_El.BotShLowHeight.value + 45.5
    if name == "BotShLowHeight":
        build_El.BeamHeight.value = value + build_El.TopShHeight.value + \
                                    build_El.RibHeight.value + build_El.BotShUpHeight.value
        if build_El.BotShUpHeight.value + value + 45.5 > build_El.HoleHeight.value:
            build_El.HoleHeight.value = build_El.BotShUpHeight.value + value + 45.5
def variation_hole(build_El, name, value):
    if name == "HoleHeight":
        if value > build_El.BeamHeight.value - build_El.TopShHeight.value - 45.5:
            build_El.HoleHeight.value = build_El.BeamHeight.value - build_El.TopShHeight.value - 45.5
        elif value < build_El.BotShLowHeight.value + build_El.BotShUpHeight.value + 45.5:
            build_El.HoleHeight.value = build_El.BotShLowHeight.value + build_El.BotShUpHeight.value + 45.5
    if name == "HoleDepth":
        if value >= build_El.BeamLength.value / 2.:
            build_El.HoleDepth.value = build_El.BeamLength.value / 2. - 45.5
