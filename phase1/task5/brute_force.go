package main

import(
    "fmt"
    "crypto/aes"
    "crypto/cipher"
    "strings"
    "io/ioutil"
    "log"
)

func main() {
    // read in encrypted log
    file_contents, err := ioutil.ReadFile("Logs/20200628_153027.log")
    if err != nil {
        log.Fatal(err)
    }

    // get a few blocks
    ciphertext := file_contents[:160]
    plaintext := make([]byte, 160)

    // latitude degrees
    for kd := 0; kd <= 90; kd++ {
        fmt.Println("Latitude Degrees (0-90):", kd)
        // latitude minutes
        for km := 0; km <= 60; km++ {
            // zero pad to match ddmm and dddmmm format
            key_base := fmt.Sprintf("%02d%02d", kd, km)
            // Turns out IV is unnecessary! 
            iv_base := fmt.Sprintf("%03d%02d", 0, 0)

            // generate key just like gpslogger does
            key := strings.Repeat(key_base, 4)
            iv := strings.Repeat(iv_base, 3) + "0"

            // make cipher just like gpslogger
            x, err := aes.NewCipher([]byte(key))
            if err != nil {
                log.Fatal(err)
            }
            dec := cipher.NewCBCDecrypter(x, []byte(iv))

            dec.CryptBlocks(plaintext, ciphertext)

            // likely going to see the 'start of sentence' symbol ($)
            if plaintext[0] != '$' {
                continue
            }
            // test to make sure first few bytes are printable and all that
            for index, test := range plaintext {
                if test > 128 || test < 8 {
                    break
                }

                if index == 32 {
                    // good chance it will work
                    //fmt.Println(kd, km, id, im, string(plaintext))
                    fmt.Println(kd, km, string(plaintext))
                    return 
                }
            }
        }
    }
}
