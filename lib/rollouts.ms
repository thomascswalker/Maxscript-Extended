rFileIn @"values.ms"

struct ControlResizerStruct (

)

struct RolloutBuilderStruct (
private

    kRoot      = Dictionary #string,
    kDialog    = Dictionary #string,
    kTitle     = "Main Window",
    kLayout    = "grid",
    kSize      = Point2 640 480,
    kResizable = false,
    kControls  = #(),

    kBuildGlobalPrefix = "rbg_",
    kBuildRolloutName  = "",

    kBuildString     = StringStream "",
    kBuildControls   = #(),
    kBuildEvents     = #(),

    kGridRows        = 0,
    kGridColumns     = 0,
    kGridColumnWidth = 0,
    kGridRowHeight   = 0,
    kControlInitX    = 5,
    kControlInitY    = 5,
    kControlGap      = 20,
    kControlHeight   = 20,
    kRolloutWidth    = 0,
    kRolloutHeight   = 0,

    fn GetControlWidth       = ((kRolloutWidth as float  / kGridColumns as float) - kControlGap as float),
    fn GetControlHeight      = ((kRolloutHeight as float / kGridRows as float)    - kControlGap as float),
    fn GetControlPosX column = (kControlInitX + (column * kGridColumnWidth) - kGridColumnWidth),
    fn GetControlPosY row    = (kControlInitY + (row * kGridRowHeight) - kGridRowHeight),

    /*
     * Builds the 
     * @param <string> filename - The full address of the .json file to load the UI from.
     * @returns <void>
     */
    fn AddControl ctl = (
        local controlStr = StringStream ""

        local ctlClass  = ctl.v2["class"]
        local ctlName   = ctl.v1
        local ctlText   = ctl.v2["text"]
        local ctlFn     = ctl.v2["action"]
        local ctlEvent  = case (ctlClass) of (
                            "button": "pressed"
                        )
        local ctlWidth  = GetControlWidth()
        local ctlHeight = GetControlHeight()
        local ctlPosX   = GetControlPosX ctl.v2["column"] 
        local ctlPosY   = GetControlPosY ctl.v2["row"]

        format "% % \"%\" width:% height:% pos:[%,%]\n" ctlClass ctlName ctlText ctlWidth ctlHeight ctlPosX ctlPosY to:controlStr
        format "on % % do (%)\n" ctlName ctlEvent ctlFn to:controlStr

        format "\n%" (controlStr as string) to:kBuildString
    ),

public

    /*
     * Initializes the variables from the provided .json file.
     * @param <string> filename - The full address of the .json file to load the UI from.
     * @returns <void>
     */
    fn SetLayoutFromFile filename = (
        kRoot     = readJson filename
        kDialog   = kRoot["dialog"]
        kTitle    = kRoot["dialog"]["properties"]["title"]
        kLayout   = kRoot["dialog"]["layout"]
        kRolloutWidth = kDialog["geometry"]["width"]
        kRolloutHeight = kDialog["geometry"]["height"]
        kSize     = Point2 kDialog["geometry"]["width"] kDialog["geometry"]["height"]
        kResizable   = kRoot["dialog"]["properties"]["resizable"]
        kControls = kRoot["dialog"]["controls"]

        kBuildRolloutName = kBuildGlobalPrefix + (SubstituteString kTitle " " "")

        for ctl in kControls do (
            if (ctl.v2["row"] > kGridRows) then (kGridRows = ctl.v2["row"])
            if (ctl.v2["column"] > kGridColumns) then (kGridColumns = ctl.v2["column"])
        )

        kGridColumnWidth = kRolloutWidth as float / kGridColumns
        kGridRowHeight = kRolloutHeight as float / kGridRows
    ),

    fn ResizeControls controls = (
        for ctl in controls do (
            local ctlWidth  = GetControlWidth()
            local ctlHeight = GetControlHeight()
            local ctlPosX   = GetControlPosX ctl.v2["column"] 
            local ctlPosY   = GetControlPosY ctl.v2["row"]

            ctl.width       = ctlWidth
            ctl.height      = ctlHeight
            ctl.pos         = [ctlPosX, ctlPosY]
        )
    ),

    fn GetControls = (kControls),

    fn Build = (
        format "global %\n" kBuildRolloutName to:kBuildString
        format "rollout % \"%\" (\n" kBuildRolloutName kTitle to:kBuildString
        format "local this = %\n" kBuildRolloutName to:kBuildString

        for ctl in kControls do (AddControl ctl)

        format "on % resized size do rb.ResizeControls %\n" kBuildRolloutName #(kControls) to:kBuildString
        format ")" to:kBuildString

        print kBuildString

        execute (kBuildString as string)
    ),

    fn Show = (
        local showStr = StringStream ""

        local style = #(#style_titlebar, #style_border, #style_sysmenu)
        if (kResizable) then (append style #style_resizing)

        print style
        print kResizable

        format "DestroyDialog %\n" kBuildRolloutName to:showStr
        format "CreateDialog % width:% height:% style:%" kBuildRolloutName kSize[1] kSize[2] (style as string) to:showStr

        this.Close()
        execute (showStr as string)
    ),

    fn Close = (
        local closeStr = StringStream ""

        format "DestroyDialog %" kBuildRolloutName to:closeStr

        execute (closeStr as string)
    )
)

-- Example
::rb = RolloutBuilderStruct()
rb.Close()
rb.SetLayoutFromFile @"..\ui\basicdialog.json"
rb.Build()
rb.Show()