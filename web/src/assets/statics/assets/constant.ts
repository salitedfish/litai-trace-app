export const WEILAILINE = '200803L0001'
export const HUAWEILINE = '200803L0006'

export const XIAOPENGLINE = '200803L0002'

export const GUNCHILINE1 = '200101L0001'
export const GUNCHILINE2 = '200101L0002'
export const GUNCHILINE3 = '200101L0003'
export const GUNCHILINE4 = '200101L0004'
export const DIANCHI2LINE = '200303L0001'

export const BOLENG = 'boleng'

const GUNCHILINELAYOUT = [
    [0],
    [1],
    [2],
    [3],
    [4]
]

export const RENDERNUM = {
    [XIAOPENGLINE]: [
        [0, 3],
        [1],
        [2, 4],
        [5, 6]
    ],
    [WEILAILINE]: [
        [0, 1],
        [2],
        [3],
        [4],
        [5, 6],
        [7],
        [8]
    ],
    [HUAWEILINE]: [
        [0, 1],
        [2],
        [3],
        [4],
        [5, 6],
        [7],
        [8]
    ],
    [GUNCHILINE1]: GUNCHILINELAYOUT,
    [GUNCHILINE2]: GUNCHILINELAYOUT,
    [GUNCHILINE3]: GUNCHILINELAYOUT,
    [GUNCHILINE4]: GUNCHILINELAYOUT,
    [DIANCHI2LINE]: [
        [0, 1],
        [2],
        [3],
        [4],
        [5, 6],
        [7],
        [8]
    ],
    [DIANCHI2LINE + '_Simple']: [
        [0],
        [1],
        [2],
        [3, 4, 5]
    ],
    [BOLENG]: [
        [0, 1],
        [2, 3],
        [4, 5],
        [6]
    ]
}

export const WARNINGLIST: {
    name: string,
    value: string,
    color: string
}[] = [
    {
        name: '预警',
        value: 'warnCount',
        color: '#FFC117'
    },
    {
        name: '告警',
        value: 'foreWarnCount',
        color: '#FF7600'
    },
    {
        name: '升级告警',
        value: 'upgradeWarnCount',
        color: '#FF4417'
    },
    {
        name: '已解决',
        value: 'solvedCount',
        color: '#17FFB8'
    }
]

export const TOPDIVLIST: string[] = ['top-left', 'top-center', 'top-right']

export const MIDDLEDIVLIST: string[] = ['middle-left', 'middle-center', 'middle-right']
