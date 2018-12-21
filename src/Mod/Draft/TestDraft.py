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

import FreeCAD, os, unittest, FreeCADGui, Draft
from Draft import svg


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
