import pcbnew

def plot_board(board_file, output_dir):
    board = pcbnew.LoadBoard(board_file)
    
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()
    
    plot_options.SetOutputDirectory(output_dir)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetLineWidth(pcbnew.FromMM(0.1))
    plot_options.SetAutoScale(False)
    plot_options.SetScale(1)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetExcludeEdgeLayer(True)
    plot_options.SetUseAuxOrigin(True)
    plot_options.SetPlotReference(True)
    plot_options.SetPlotValue(True)
    plot_options.SetPlotInvisibleText(False)
    plot_options.SetDrillMarksType(pcbnew.PCB_PLOT_PARAMS.NO_DRILL_SHAPE)
    plot_options.SetSubtractMaskFromSilk(False)
    plot_options.SetOutputFormat(pcbnew.PLOT_FORMAT_PDF)
    
    plot_plan = [
        (pcbnew.F_Cu, "F_Cu"),
        (pcbnew.B_Cu, "B_Cu"),
        (pcbnew.F_SilkS, "F_SilkS"),
        (pcbnew.B_SilkS, "B_SilkS"),
    ]
    
    for layer_info in plot_plan:
        plot_controller.SetLayer(layer_info[0])
        plot_controller.OpenPlotfile(layer_info[1], pcbnew.PLOT_FORMAT_PDF, layer_info[1])
        plot_controller.PlotLayer()
    
    plot_controller.ClosePlot()

if __name__ == "__main__":
    board_file = "/home/jack/SMEG/opm_coil_fork.kicad_pcb"
    output_dir = "/home/jack/SMEG/opm_coil_fork"
    plot_board(board_file, output_dir)
