description = 'preset values for the sample position'
group = 'configdata'

#open_pos_mir_ap2  = (0, 3, 75, 20)
# with 2.2T JEM:
open_pos_mir_ap2  = (0, 3.0, 80, 20)
open_pos_sam10_ap = (0, 0, 100,  83)
open_pos_sam01_ap = (0, 0, 25,  25)


#open_pos_sam10_ap = (1, -11.5, 27,  22)


dock_pos_sam10_x = 150.000
dock_pos_sam10_y = 5.000

dock_pos_sam01_x = 150.00
dock_pos_sam01_y = 30.00

SAMPLE_POS_PRESETS = {
    # TODO: add proper presets
    '10m': dict(
        active_ap = 'mir_ap2',
        active_x = 'sam10_x',
        active_y = 'sam10_y',

        sam10_ap = open_pos_sam10_ap,
#        sam01_ap = open_pos_sam01_ap,
        sam01_x = dock_pos_sam01_x,
        sam01_y = dock_pos_sam01_y,
    ),
    '9.5m': dict(
        active_ap = 'sam10_ap',
        active_x = 'sam10_x',
        active_y = 'sam10_y',

        mir_ap2 = open_pos_mir_ap2,
#        sam01_ap = open_pos_sam01_ap,
        sam01_x = dock_pos_sam01_x,
        sam01_y = dock_pos_sam01_y,
    ),
    '3m': dict(
        active_ap = 'mir_ap2',
        active_x = 'sam01_x',
        active_y = 'sam01_y',

        sam10_ap = open_pos_sam10_ap,

        sam10_x = dock_pos_sam10_x,
        sam10_y = dock_pos_sam10_y,

#        sam01_x = dock_pos_sam01_x,
#        sam01_y = dock_pos_sam01_y,
    ),
    '1.3m': dict(
        active_ap = 'sam01_ap',
        active_x = 'sam01_x',
        active_y = 'sam01_y',

        mir_ap2 = open_pos_mir_ap2,
        sam10_ap = open_pos_sam10_ap,
        sam10_x = dock_pos_sam10_x,
        sam10_y = dock_pos_sam10_y,
    ),
    '0.15m': dict(
        active_ap = 'sel_ap2',
        active_x = 'sam01_x',
        active_y = 'sam01_y',

        mir_ap2 = open_pos_mir_ap2,
#        sam01_ap = open_pos_sam01_ap,
        sam10_ap = open_pos_sam10_ap,
        sam10_x = dock_pos_sam10_x,
        sam10_y = dock_pos_sam10_y,
    )
}
