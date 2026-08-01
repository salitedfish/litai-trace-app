import axios from 'http/serverRequests'
import { AxiosRequestConfig } from 'axios'

// 判断数据是否为对象
function isObject (value: any): boolean {
    let result: string = Object.prototype.toString.call(value)
    return result === '[object Object]'
}

function httpHelp<T = any> (methods: string, param?: any, config?: AxiosRequestConfig): Promise<T> {
    return new Promise((resolve, reject) => {
        axios[methods](...[...(param !== undefined ? [param] : []), res => {
            if (res.code !== 'fail') {
                if (Object.prototype.toString.call(res.data) === '[object Blob]') {
                    resolve(res)
                } else {
                    resolve(res.data)
                }
            } else {
                reject(res.info)
            }
        }, err => {
            reject(err)
        }, config || {}])
    })
}

function generateLighterColors (color: string): string[] {
    let r: number, g: number, b: number, a: number

    if (color.startsWith('#')) {
        color = color.slice(1)
        if (color.length === 3) {
            color = color
                .split('')
                .map((c) => c + c)
                .join('')
        }

        r = parseInt(color.substr(0, 2), 16)
        g = parseInt(color.substr(2, 2), 16)
        b = parseInt(color.substr(4, 2), 16)
    } else if (color.startsWith('rgba')) {
        const rgba = color.match(/\d+(\.\d+)?/g)
        r = parseInt(rgba![0], 10)
        g = parseInt(rgba![1], 10)
        b = parseInt(rgba![2], 10)
        a = parseFloat(rgba![3])
    } else {
        throw new Error('Invalid color format')
    }

    const lighterColors: string[] = []

    for (let i = 4; i < 5; i++) {
        const factor = 1 + i * 0.2 // 调整因子，用于控制颜色变浅程度
        const newR = Math.round(r * factor)
        const newG = Math.round(g * factor)
        const newB = Math.round(b * factor)

        // @ts-ignore
        const rgba = a !== undefined ? `rgba(${newR}, ${newG}, ${newB}, ${a * (1 - i * 0.15)})` : `rgba(${newR}, ${newG}, ${newB})`
        lighterColors.push(rgba)
    }

    return lighterColors
}

export {
    isObject,
    generateLighterColors,
    httpHelp
}
