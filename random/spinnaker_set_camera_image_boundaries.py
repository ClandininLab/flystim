import PySpin


system = PySpin.System.GetInstance()

cam_list = system.GetCameras()
assert cam_list.GetSize() == 1
cam = cam_list[0]

cam.Init()
nodemap = cam.GetNodeMap()
#node_image_format_control = nodemap.GetNode("ImageFormatControl")
#[x.GetDisplayName() for x in PySpin.CCategoryPtr(node_image_format_control).GetFeatures()]
PySpin.CIntegerPtr(nodemap.GetNode("Width")).SetValue(752)
PySpin.CIntegerPtr(nodemap.GetNode("Height")).SetValue(616)
PySpin.CIntegerPtr(nodemap.GetNode("OffsetX")).SetValue(328)
PySpin.CIntegerPtr(nodemap.GetNode("OffsetY")).SetValue(336)

#cam.DeInit()



#node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
#node_pixel_format_raw8 = PySpin.CEnumEntryPtr(node_pixel_format.GetEntryByName('Raw8'))
#if PySpin.IsAvailable(node_pixel_format_raw8) and PySpin.IsReadable(node_pixel_format_raw8):
#    pixel_format_raw8 = node_pixel_format_raw8.GetValue()
#    node_pixel_format.SetIntValue(pixel_format_raw8)
#    print('Pixel format set to %s...' % node_pixel_format.GetCurrentEntry().GetSymbolic())
#else:
#    print('Pixel format raw 8 not available...')

#[x.GetDisplayName() for x in node_pixel_format.GetEntries()]
