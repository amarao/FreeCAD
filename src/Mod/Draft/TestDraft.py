# Unit test for the Draft module

#***************************************************************************
#*   (c) Yorik van Havre <yorik@uncreated.net> 2013                        *
#*                                                                         *
#*   This file is part of the FreeCAD CAx development system.              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   FreeCAD is distributed in the hope that it will be useful,            *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with FreeCAD; if not, write to the Free Software        *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************/

import FreeCAD
import unittest
import FreeCADGui
import Draft
import re
from Draft import svg


class GetSVGTest_path(unittest.TestCase):
    def test_good_empty(self):
        with svg.path() as path:
            pass
        self.assertEqual(path.d, "")

    def test_good_one_lineto(self):
        with svg.path() as path:
            path.lineto(svg.Vector(0, 0, 0))
        self.assertEqual(path.d, "M 0.0 0.0")

    def test_good_two_lineto(self):
        with svg.path() as path:
            path.lineto(svg.Vector(0, 0, 0))
            path.lineto(svg.Vector(1, 1, 0))
        self.assertEqual(path.d, "M 0.0 0.0 L 1.0 1.0")

    def test_good_three_lineto(self):
        with svg.path() as path:
            path.lineto(svg.Vector(0, 0, 0))
            path.lineto(svg.Vector(10, 1, 0))
            path.lineto(svg.Vector(0, -10, 0))
        self.assertEqual(path.d, "M 0.0 0.0 L 10.0 1.0 L 0.0 -10.0")

    def test_good_horizontal_lineto(self):
        with svg.path() as path:
            path.moveto(svg.Vector(0, 0, 0))
            path.horizontal_lineto(3)
            path.moveto(svg.Vector(0, -10, 0))
            path.horizontal_lineto(-1)
            path.horizontal_lineto(-1)
        self.assertEqual(path.d, "M 0.0 0.0 H 3.0 M 0.0 -10.0 H -1.0 H -1.0")

    def test_good_vertical_lineto(self):
        with svg.path() as path:
            path.moveto(svg.Vector(0, 0, 0))
            path.vertical_lineto(3)
            path.moveto(svg.Vector(0, -10, 0))
            path.vertical_lineto(-1)
            path.vertical_lineto(-1)
        self.assertEqual(path.d, "M 0.0 0.0 V 3.0 M 0.0 -10.0 V -1.0 V -1.0")

    def test_good_append_data(self):
        with svg.path() as path1:
            path1.moveto(svg.Vector(0, 0, 0))
            path1.lineto(svg.Vector(1, 1, 0))
        with svg.path() as path2:
            path2.moveto(svg.Vector(0, -10, 0))
            path2.lineto(svg.Vector(2, 2, 0))
        path1.append_data(path2)
        self.assertEqual(path1.d, "M 0.0 0.0 L 1.0 1.0 M 0.0 -10.0 L 2.0 2.0")

    def test_bad_no_moveto_at_begining(self):
        with self.assertRaises(ValueError):
            with svg.path() as path:
                path.horizontal_lineto(1)

    def test_bad_context_manager_passes_exception(self):
        with self.assertRaises(AttributeError):
            with svg.path() as path:
                path.moveto(dict)


class GetSVGTest_getDraftParam(unittest.TestCase):

    def test_good_svgDashedLine(self):
        self.assertEqual(svg.getDraftParam('svgDashedLine', '1'), '1')

    def test_good_svgDottedLine(self):
        self.assertEqual(svg.getDraftParam('svgDottedLine', '1'), '1')

    def test_good_svgDashdotLine(self):
        self.assertEqual(svg.getDraftParam('svgDashdotLine', '1'), '1')

    def test_good_svgDiscretization(self):
        self.assertEqual(svg.getDraftParam('svgDiscretization', 1.0), 1.0)

    def test_sad_exception(self):
        with self.assertRaises(ValueError):
            svg.getDraftParam('foobar', "foobar")


class GetSVGTest_process_custom_linestyle(unittest.TestCase):

    def test_good_no_scale(self):
        self.assertEqual(
            svg.process_custom_linestyle("1,1,1", 1),
            "1.0,1.0,1.0"
        )

    def test_good_int_division(self):
        self.assertEqual(
            svg.process_custom_linestyle("5,2,0.1", 2),
            "2.5,1.0,0.05"
        )

    def test_good_float_division(self):
        self.assertEqual(
            svg.process_custom_linestyle("4.0,2.0,1.0", 2.0),
            "2.0,1.0,0.5"
        )

    def test_good_negative_and_zero(self):
        self.assertEqual(
            svg.process_custom_linestyle("-1,0,-0.5", 5),
            "-0.2,0.0,-0.1"
        )

    def test_sad_empty(self):
        self.assertEqual(svg.process_custom_linestyle("", 5), "none")

    def test_sad_no_coma(self):
        self.assertEqual(svg.process_custom_linestyle("5", 5), "none")

    def test_sad_NaN(self):
        self.assertEqual(svg.process_custom_linestyle("Nan,NaN", 5), "none")

    def test_sad_Inf(self):
        self.assertEqual(svg.process_custom_linestyle("Inf,Inf", 5), "none")

    def test_sad_stings(self):
        self.assertEqual(svg.process_custom_linestyle("One,Two", 5), "none")

    def test_sad_scale_type(self):
        self.assertEqual(svg.process_custom_linestyle("1,2", "wrong"), "none")

    def test_bad_input_type(self):
        with self.assertRaises(Exception):
            svg.process_custom_linestyle(dict, 2)


class GetSVGTest_getLineStyle(unittest.TestCase):

    def test_good_dashed(self):
        self.assertEqual(svg.getLineStyle("Dashed", 1), "0.09,0.05")

    def test_good_dashdot(self):
        self.assertEqual(svg.getLineStyle("Dashdot", 1), "0.09,0.05,0.02,0.05")

    def test_good_dotted(self):
        self.assertEqual(svg.getLineStyle("Dotted", 1), "0.02,0.02")

    def test_good_known_ignore_scale(self):
        self.assertEqual(svg.getLineStyle("Dotted", 2), "0.02,0.02")

    def test_good_custom_no_scale(self):
        self.assertEqual(svg.getLineStyle("1.0,2.0", 1.0), "1.0,2.0")

    def test_good_custom_scale(self):
        self.assertEqual(svg.getLineStyle("1.0,2.0", 2.0), "0.5,1.0")

    def test_sad_bad_style(self):
        self.assertEqual(svg.getLineStyle("fobar", 2.0), "none")


class GetSVGTest_getPattern(unittest.TestCase):

    def test_good_pattern_present(self):
        self.assertTrue('concrete' in svg.getPattern('concrete'))

    def test_sad_pattern_not_present(self):
        self.assertEqual(svg.getPattern('non_existing_foobar'), '')


class getSVGTest_projected_length(unittest.TestCase):

    def test_good_no_flipping(self):
        self.assertEqual(
            svg.projected_length(
                svg.Vector(1, 0, 0),
                svg.Vector(1, 0, 0)
            ),
            1.0
        )

    def test_good_flipping(self):
        self.assertEqual(
            svg.projected_length(
                svg.Vector(-1, 0, 0),
                svg.Vector(1, 0, 0)
            ),
            -1.0
        )

    def test_good_zero_projection(self):
        self.assertEqual(
            svg.projected_length(
                svg.Vector(0, 0, 1),
                svg.Vector(1, 0, 0)
            ),
            0.0
        )


class GetSVGTest_getProj(unittest.TestCase):
    def test_good_no_plane(self):
        self.assertEqual(
            svg.getProj(svg.Vector(0.0, 1.0, 2.0), None),
            svg.Vector(0.0, 1.0, 2.0)
        )

    def test_good_collinear(self):
        vect = svg.Vector(1, 0, 0)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            vect
        )

    def test_good_negative_collinear(self):
        vect = svg.Vector(-1, 0, 0)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            vect
        )

    def test_good_planar(self):
        vect = svg.Vector(2, 3, 0)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            vect
        )

    def test_good_normal(self):
        vect = svg.Vector(0, 0, -1)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            svg.Vector(0, 0, 0)
        )

    def test_good_zero(self):
        vect = svg.Vector(0, 0, 0)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            svg.Vector(0, 0, 0)
        )

    def test_good_45_degree(self):
        vect = svg.Vector(1, 1, 1)
        plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.assertEqual(
            svg.getProj(vect, plane),
            svg.Vector(1, 1, 0)
        )

    def test_good_non_default_axis(self):
        vect = svg.Vector(9, 8, 7)
        plane = svg.WorkingPlane.plane(
            svg.Vector(3.33, 1.11, 4),
            svg.Vector(12, 42, -2),
            svg.Vector(-1, -1, -1)
        )
        proj = svg.getProj(vect, plane)
        self.assertAlmostEqual(proj.x, 12.56166246)
        self.assertAlmostEqual(proj.y, 9.833871105)


class GetSVGTest_getDiscretized(unittest.TestCase):

    doc_name = "GetSVGTest_getDiscretized"

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != self.doc_name:
                FreeCAD.newDocument(self.doc_name)
        else:
            FreeCAD.newDocument(self.doc_name)
        FreeCAD.setActiveDocument(self.doc_name)
        self.plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )

    def tearDown(self):
        FreeCAD.closeDocument(self.doc_name)

    def test_good_line(self):
        wire = Draft.makeWire([
            FreeCAD.Vector(0, 0, 0),
            FreeCAD.Vector(2, 0, 0)
        ])
        edges = wire.Shape.Edges
        self.assertEqual(
            svg.getDiscretized(edges[0], self.plane),
            "M -0.0 -0.0 L 2.0 -0.0"
        )


class GetSVGTest_get_drawing_plane_normal(unittest.TestCase):

    doc_name = "GetSVGTest_get_drawing_plane_normal"

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != self.doc_name:
                FreeCAD.newDocument(self.doc_name)
        else:
            FreeCAD.newDocument(self.doc_name)
        FreeCAD.setActiveDocument(self.doc_name)
        self.plane = svg.WorkingPlane.plane(
            svg.Vector(1, 1, 0),
            svg.Vector(0, 1, 1),
            svg.Vector(1, 0, 1)
        )

    def tearDown(self):
        FreeCAD.closeDocument(self.doc_name)

    def test_good_plane(self):
        self.assertEqual(
            svg.get_drawing_plane_normal(self.plane),
            FreeCAD.Vector(1, 0, 1)
        )

    def test_good_nothing_available(self):
        self.assertEqual(
            svg.get_drawing_plane_normal(None),
            FreeCAD.Vector(0, 0, 1)
        )

    def test_good_draft_working_plane(self):
        FreeCAD.DraftWorkingPlane.alignToPointAndAxis(
            FreeCAD.Vector(-1, 0, 0),
            FreeCAD.Vector(0, -1, 0),
            0
        )
        self.assertEqual(
            svg.get_drawing_plane_normal(None),
            FreeCAD.Vector(0, -1, 0)
        )


class GetSVGTest_getPath(unittest.TestCase):

    doc_name = "GetSVGTest_getPath"

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != self.doc_name:
                FreeCAD.newDocument(self.doc_name)
        else:
            FreeCAD.newDocument(self.doc_name)
        FreeCAD.setActiveDocument(self.doc_name)
        self.plane = svg.WorkingPlane.plane(
            svg.Vector(1, 0, 0),
            svg.Vector(0, 1, 0),
            svg.Vector(0, 0, 1)
        )
        self.placement = FreeCAD.Placement()
        self.placement.Rotation.Q = (0.0, 0.0, 1.5, 1.0)
        self.placement.Base = FreeCAD.Vector(-1.5, -1.0, 0.0)

    def tearDown(self):
        FreeCAD.closeDocument(self.doc_name)

    def defuzzy(self, string):
        '''
            To keep original output data pristine, we clearing out some
            fuzziness in output (double spaces, spaces before quotation, etc)
        '''
        no_linefeeds = re.sub('\n', '', string)
        no_double_spaces = re.sub('\s+', ' ', no_linefeeds)
        no_spaces_before_quotes = re.sub(' "', '"', no_double_spaces)
        no_spaces_after_quotes = re.sub('" ', '"', no_spaces_before_quotes)
        no_spaces_before_end = re.sub(' /', '/', no_spaces_after_quotes)
        no_spaces_after_semi = re.sub('; ', ';', no_spaces_before_end)
        no_spaces_after_column = re.sub(': ', ':', no_spaces_after_semi)
        return no_spaces_after_column

    def test_good_rectangle(self):
        rec = Draft.makeRectangle(
            length=4,
            height=2,
            placement=self.placement,
            face=False,
            support=None
        )
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=rec,
                    pathdata=[],
                    edges=rec.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="Rectangle"
                    d="M -1.5 -1.0 L -3.03846153846 2.69230769231
                        L -4.88461538462 1.92307692308
                        L -3.34615384615 -1.76923076923
                        L -1.5 -1.0 " stroke="#000000"
                    stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                        stroke-dasharray:none;fill:none;
                        fill-rule: evenodd "/>\n'''
            )
        )

    def test_good_rectangle_face(self):
            rec = Draft.makeRectangle(
                length=4,
                height=2,
                placement=self.placement,
                face=True,
                support=None
            )
            self.assertEqual(
                self.defuzzy(
                    svg.getPath(
                        plane=self.plane,
                        fill="#CCCCCC",
                        stroke="#000000",
                        linewidth=0.21,
                        lstyle="none",
                        obj=rec,
                        pathdata=[],
                        edges=rec.Shape.Edges,
                        wires=[],
                        pathname=None
                    )
                ),
                self.defuzzy(
                    '''<path id="Rectangle"
                        d="M -1.5 -1.0
                            L -3.03846153846 2.69230769231
                            L -4.88461538462 1.92307692308
                            L -3.34615384615 -1.76923076923
                            L -1.5 -1.0 Z "
                        stroke="#000000" stroke-width="0.21 px"
                        style="stroke-width:0.21;stroke-miterlimit:4;
                            stroke-dasharray:none;fill:#CCCCCC;
                            fill-rule: evenodd "/>\n'''
                )
            )

    def test_good_circle(self):
        placement = FreeCAD.Placement()
        placement.Rotation.Q = (0.0, 0.0, 1.5, 1.0)
        placement.Base = FreeCAD.Vector(-1.5, -1.0, 0.0)
        circle = Draft.makeCircle(radius=3, placement=placement, face=None)
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=circle,
                    pathdata=[],
                    edges=circle.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<circle cx="-1.5" cy="-1.0"
                    r="3.0" stroke="#000000"
                    stroke-width="0.21 px" style="stroke-width:0.21;
                    stroke-miterlimit:4;stroke-dasharray:none;fill:none"/>\n'''
            )
        )

    def test_good_ellipse(self):
        placement = FreeCAD.Placement()
        placement.Rotation.Q = (0.0, 0.0, 1.5, 1.0)
        placement.Base = FreeCAD.Vector(-1.5, -1.0, 0.0)
        ellipse = Draft.makeEllipse(
            majradius=3,
            minradius=2,
            placement=placement,
            face=None
        )
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=ellipse,
                    pathdata=[],
                    edges=ellipse.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="Ellipse"
                    d="M -2.65384615385 1.76923076923
                     A 3.0 2.0 -67.380135052 0 0 -0.346153846154 -3.76923076923
                     A 3.0 2.0 -67.380135052 0 0 -2.65384615385 1.76923076923 "
                    stroke="#000000" stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                        stroke-dasharray:none;fill:none;
                        fill-rule: evenodd "/>\n'''
            )
        )


    def test_good_bez1(self):
        points = [
            FreeCAD.Vector(-1, 1, 0.0),
            FreeCAD.Vector(-3, 5, 0.0)
        ]
        bez = Draft.makeBezCurve(points, closed=False, support=None)
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=bez,
                    pathdata=[],
                    edges=bez.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="Line"
                    d="M -1.0 1.0 L -3.0 5.0 "
                    stroke="#000000" stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                        stroke-dasharray:none;fill:none;
                        fill-rule: evenodd "/>\n'''
            )
        )

    def test_good_bez2(self):
        points = [
            FreeCAD.Vector(-1, 1, 0.0),
            FreeCAD.Vector(-3, 5, 0.0),
            FreeCAD.Vector(5, 2, 0.0)
        ]
        bez = Draft.makeBezCurve(points, closed=False, support=None)
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=bez,
                    pathdata=[],
                    edges=bez.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="BezCurve"
                    d="M -1.0 1.0 Q -3.0 5.0 5.0 2.0 "
                    stroke="#000000" stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                    stroke-dasharray:none;fill:none;fill-rule: evenodd "/>\n'''
            )
        )

    def test_good_bez3(self):
        points = [
            FreeCAD.Vector(-1, 1, 0),
            FreeCAD.Vector(-3, 5, 0),
            FreeCAD.Vector(5, 2, 0),
            FreeCAD.Vector(0, 0, 0),
        ]
        bez = Draft.makeBezCurve(points, closed=False, support=None)
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=bez,
                    pathdata=[],
                    edges=bez.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="BezCurve"
                    d="M -1.0 1.0 C -3.0 5.0 5.0 2.0 -0.0 -0.0 "
                    stroke="#000000" stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                        stroke-dasharray:none;fill:none;
                        fill-rule: evenodd "/>\n'''
            )
        )

    def test_good_bspline(self):
        points = [
            FreeCAD.Vector(-1, 1, 0),
            FreeCAD.Vector(-3, 5, 0),
            FreeCAD.Vector(5, 2, 0),
            FreeCAD.Vector(0, 0, 0),
        ]
        spline = Draft.makeBSpline(points, closed=False, support=None)
        self.assertEqual(
            self.defuzzy(
                svg.getPath(
                    plane=self.plane,
                    fill="none",
                    stroke="#000000",
                    linewidth=0.21,
                    lstyle="none",
                    obj=spline,
                    pathdata=[],
                    edges=spline.Shape.Edges,
                    wires=[],
                    pathname=None
                )
            ),
            self.defuzzy(
                '''<path id="BSpline"
                    d="M -1.0 1.0 C -3.50786585035 3.41567830625
                        -3.78539976065 4.59632533295 -3.0 5.0
                        C -1.49949586414 5.77121936852 3.8807161707
                        3.70648962432 5.0 2.0 C 5.70546877862
                        0.924423707838 4.71824005093 -0.00883801614885
                        -0.0 -0.0 " stroke="#000000"
                    stroke-width="0.21 px"
                    style="stroke-width:0.21;stroke-miterlimit:4;
                    stroke-dasharray:none;fill:none;fill-rule: evenodd "/>\n'''
                )
        )


class DraftTest(unittest.TestCase):

    def setUp(self):
        # setting a new document to hold the tests
        if FreeCAD.ActiveDocument:
            if FreeCAD.ActiveDocument.Name != "DraftTest":
                FreeCAD.newDocument("DraftTest")
        else:
            FreeCAD.newDocument("DraftTest")
        FreeCAD.setActiveDocument("DraftTest")

    def testPivy(self):
        FreeCAD.Console.PrintLog ('Checking Pivy...\n')
        from pivy import coin
        c = coin.SoCube()
        FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(c)
        self.failUnless(c,"Pivy is not working properly")

    # creation tools

    def testLine(self):
        FreeCAD.Console.PrintLog ('Checking Draft Line...\n')
        Draft.makeLine(FreeCAD.Vector(0,0,0),FreeCAD.Vector(-2,0,0))
        self.failUnless(FreeCAD.ActiveDocument.getObject("Line"),"Draft Line failed")

    def testWire(self):
        FreeCAD.Console.PrintLog ('Checking Draft Wire...\n')
        Draft.makeWire([FreeCAD.Vector(0,0,0),FreeCAD.Vector(2,0,0),FreeCAD.Vector(2,2,0)])
        self.failUnless(FreeCAD.ActiveDocument.getObject("Wire"),"Draft Wire failed")

    def testBSpline(self):
        FreeCAD.Console.PrintLog ('Checking Draft BSpline...\n')
        Draft.makeBSpline([FreeCAD.Vector(0,0,0),FreeCAD.Vector(2,0,0),FreeCAD.Vector(2,2,0)])
        self.failUnless(FreeCAD.ActiveDocument.getObject("BSpline"),"Draft BSpline failed")

    def testRectangle(self):
        FreeCAD.Console.PrintLog ('Checking Draft Rectangle...\n')
        Draft.makeRectangle(4,2)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Rectangle"),"Draft Rectangle failed")

    def testArc(self):
        FreeCAD.Console.PrintLog ('Checking Draft Arc...\n')
        Draft.makeCircle(2, startangle=0, endangle=90)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Arc"),"Draft Arc failed")

    def testCircle(self):
        FreeCAD.Console.PrintLog ('Checking Draft Circle...\n')
        Draft.makeCircle(3)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Circle"),"Draft Circle failed")

    def testPolygon(self):
        FreeCAD.Console.PrintLog ('Checking Draft Polygon...\n')
        Draft.makePolygon(5,5)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Polygon"),"Draft Polygon failed")

    def testEllipse(self):
        FreeCAD.Console.PrintLog ('Checking Draft Ellipse...\n')
        Draft.makeEllipse(5,3)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Ellipse"),"Draft Ellipse failed")

    def testPoint(self):
        FreeCAD.Console.PrintLog ('Checking Draft Point...\n')
        Draft.makePoint(5,3,2)
        self.failUnless(FreeCAD.ActiveDocument.getObject("Point"),"Draft Point failed")

    def testText(self):
        FreeCAD.Console.PrintLog ('Checking Draft Text...\n')
        Draft.makeText("Testing Draft")
        self.failUnless(FreeCAD.ActiveDocument.getObject("Text"),"Draft Text failed")

    #def testShapeString(self):
    # not working ATM because it needs a font file
    #    FreeCAD.Console.PrintLog ('Checking Draft ShapeString...\n')
    #    Draft.makeShapeString("Testing Draft")
    #    self.failUnless(FreeCAD.ActiveDocument.getObject("ShapeString"),"Draft ShapeString failed")

    def testDimension(self):
        FreeCAD.Console.PrintLog ('Checking Draft Dimension...\n')
        Draft.makeDimension(FreeCAD.Vector(0,0,0),FreeCAD.Vector(2,0,0),FreeCAD.Vector(1,-1,0))
        self.failUnless(FreeCAD.ActiveDocument.getObject("Dimension"),"Draft Dimension failed")

    # modification tools

    def testMove(self):
        FreeCAD.Console.PrintLog ('Checking Draft Move...\n')
        l = Draft.makeLine(FreeCAD.Vector(0,0,0),FreeCAD.Vector(-2,0,0))
        Draft.move(l,FreeCAD.Vector(2,0,0))
        self.failUnless(l.Start == FreeCAD.Vector(2,0,0),"Draft Move failed")

    def testCopy(self):
        FreeCAD.Console.PrintLog ('Checking Draft Move with copy...\n')
        l = Draft.makeLine(FreeCAD.Vector(0,0,0),FreeCAD.Vector(2,0,0))
        l2 = Draft.move(l,FreeCAD.Vector(2,0,0),copy=True)
        self.failUnless(l2,"Draft Move with copy failed")

    def testRotate(self):
        FreeCAD.Console.PrintLog ('Checking Draft Rotate...\n')
        l = Draft.makeLine(FreeCAD.Vector(2,0,0),FreeCAD.Vector(4,0,0))
        Draft.rotate(l,90)
        self.assertTrue(l.Start.isEqual(FreeCAD.Vector(0,2,0), 1e-12),"Draft Rotate failed")

    def testOffset(self):
        FreeCAD.Console.PrintLog ('Checking Draft Offset...\n')
        r = Draft.makeRectangle(4,2)
        r2 = Draft.offset(r,FreeCAD.Vector(-1,-1,0),copy=True)
        self.failUnless(r2,"Draft Offset failed")

    def testCloneOfPart(self):
        #test for a bug introduced by changes attachment code
        box = FreeCAD.ActiveDocument.addObject("Part::Box", "Box")
        clone = Draft.clone(box)
        self.failUnless(clone.hasExtension("Part::AttachExtension"))

    # modification tools

    def tearDown(self):
        FreeCAD.closeDocument("DraftTest")
        pass
