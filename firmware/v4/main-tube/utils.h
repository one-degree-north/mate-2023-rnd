#ifndef UTILS_H
#define UTILS_H

#ifndef MIN
#define MIN(a, b)       (((a) < (b)) ? (a) : (b))
#endif

#ifndef MAX
#define MAX(a, b)       (((a) > (b)) ? (a) : (b))
#endif

#ifndef ABS
#define ABS(a)          ((a) < 0 ? -(a) : (a))
#endif

bool assertRange(i32 value, i32 min, i32 max) {
    return min <= value && value <= max;
}

u8 LRC (u8* bytes, u8 length) {
    u8 LRC = 0x00;
    for (int i = 0; i < length; ++i) {
        LRC = (LRC + bytes[i]) & 0xFF;
    }
    return ((LRC ^ 0xFF) + 1) & 0xFF;
}

#endif // #ifndef UTILS_H
