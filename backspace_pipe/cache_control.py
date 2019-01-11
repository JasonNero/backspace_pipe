import pymel.core as pmc

'''
    Annahmen:
    - Source und Target sind so praepariert, dass alle Shapes ueber den ShortName ansprechbar sind
    - Shapes die gehided wurden, werden ignoriert
'''


def transfer_shading(hide=True):
    currentSel = pmc.ls(sl=True)

    debug = True
    debugList = []

    if len(currentSel) == 2:
        srcTop = currentSel[0]
        trgTop = currentSel[1]

        srcShapes = pmc.listRelatives(srcTop, allDescendents=True, shapes=True)

        shadingGroups = pmc.listConnections(srcShapes, type='shadingEngine')
        shadingGroups = list(set(shadingGroups))

        for sg in shadingGroups:
            sgShapes = sg.members()
            print("\nNow processing Shading Group: {}".format(sg))
            print(sgShapes)

            for srcShape in sgShapes:
                trgShapeList = pmc.ls(srcShape.stripNamespace())
                if len(trgShapeList) == 0:
                    continue

                for trgShape in trgShapeList:
                    try:
                        if str(trgTop) in trgShape.fullPath():

                            # Transfer Opaque and Matte
                            trgShape.setAttr("aiOpaque", srcShape.getAttr("aiOpaque"))
                            trgShape.setAttr("aiMatte", srcShape.getAttr("aiMatte"))

                            # Transfer Arnold Subdiv Settings
                            trgShape.setAttr("aiSubdivType", srcShape.getAttr("aiSubdivType"))
                            trgShape.setAttr("aiSubdivIterations", srcShape.getAttr("aiSubdivIterations"))
                            trgShape.setAttr("aiSubdivUvSmoothing", srcShape.getAttr("aiSubdivUvSmoothing"))

                            # Transfer Arnold Visibility Settings
                            trgShape.setAttr("primaryVisibility", srcShape.getAttr("primaryVisibility"))
                            trgShape.setAttr("castsShadows", srcShape.getAttr("castsShadows"))
                            trgShape.setAttr("aiVisibleInDiffuseReflection", srcShape.getAttr("aiVisibleInDiffuseReflection"))
                            trgShape.setAttr("aiVisibleInSpecularReflection", srcShape.getAttr("aiVisibleInSpecularReflection"))
                            trgShape.setAttr("aiVisibleInDiffuseTransmission", srcShape.getAttr("aiVisibleInDiffuseTransmission"))
                            trgShape.setAttr("aiVisibleInSpecularTransmission", srcShape.getAttr("aiVisibleInSpecularTransmission"))
                            trgShape.setAttr("aiVisibleInVolume", srcShape.getAttr("aiVisibleInVolume"))
                            trgShape.setAttr("aiSelfShadows", srcShape.getAttr("aiSelfShadows"))

                            # Transfer Shader Connection
                            print("Forcing {} into {}".format(str(trgShape), sg))
                            sg.forcEelement(trgShape)
                            if hide:
                                pmc.hide(srcShape.getTransform().fullPath())
                        else:
                            continue
                    except AttributeError as e:
                        debugList.append("SKIPPING {} >> {}".format(srcShape, str(e)))
                    except pmc.MayaObjectError as e:
                        debugList.append("SKIPPING {} >> {}".format(srcShape, str(e)))
                    except Exception as e:
                        debugList.append("FATAL ERROR {} >> {}".format(srcShape, str(e)))

    else:
        print("Please select your Source first and then the Target")
        return False

    if debug is True:
        print("\n## DEBUG\n#")
        for item in debugList:
            print("# " + item)
        print("#\n## DEBUG\n")


def export_abc():
    fstart = pmc.playbackOptions(query=True, animationStartTime=True)
    fend = pmc.playbackOptions(query=True, animationEndTime=True)

    roots = ""
    for item in pmc.ls(sl=True):
        roots += "-root {root} ".format(root=item.fullPath())

    name = pmc.sceneName().splitext()[0].split("/")[-1] + ".abc"
    output = pmc.sceneName().parent.parent / "Caches" / name

    args = "-frameRange {fstart} {fend} -ro -stripNamespaces -uvWrite -writeVisibility -dataFormat ogawa {roots} -file {output}".format(fstart=fstart, fend=fend, roots=roots, output=output)

    pmc.AbcExport(jobArg=args)
