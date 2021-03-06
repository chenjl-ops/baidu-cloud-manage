package baiduauth

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/Sirupsen/logrus"
	"github.com/pkg/errors"
	"github.com/thoas/go-funk"
	"net/http"
	"net/url"
	"op-bill-api/internal/pkg/apollo"
	"sort"
	"strings"
	"time"
)

// 百度云认证数据
type BaiduCloud struct {
	Url             string
	Headers         map[string]string
	Method          string
	AccessKeyID     string
	AccessKeySecret string
}


func NewBaiduCloud(url string, headers map[string]string, method string) *BaiduCloud {
	b := BaiduCloud{
		Url:             url,
		Headers:         headers,
		Method:          method,
		AccessKeyID:     apollo.Config.BaiduAccessKeyID,
		AccessKeySecret: apollo.Config.BaiduAccessKeySecret,
	}

	return &b
}

func (b *BaiduCloud) request(data map[string]interface{}, result interface{}) error {
	methods := []string{"GET", "PUT", "POST", "DELETE"}
	if funk.Contains(methods, strings.ToUpper(b.Method)) {

		bytesData, err := json.Marshal(data)
		if err != nil {
			logrus.Println("json error", err)
			return err
		} else {
			request, err := http.NewRequest(strings.ToUpper(b.Method), b.Url, bytes.NewReader(bytesData))
			if err != nil {
				logrus.Println("json error", err)
				return err
			}
			for k, v := range b.Headers {
				request.Header.Set(k, v)
			}
			request.Header.Set("authorization", b.getAuthorization())
			client := http.Client{}
			resp, err := client.Do(request)
			if err != nil {
				fmt.Println(err.Error())
				return err
			}
			err1 := json.NewDecoder(resp.Body).Decode(result)
			if err1 != nil {
				return err1
			}
			return nil
		}
	} else {
		return errors.New(fmt.Sprintf("%s not allow", b.Method))
	}
}

func (b *BaiduCloud) getAuthorization() string {
	return fmt.Sprintf("bce-auth-v1/%s/%s/1800/%s/%s", b.AccessKeyID, b.getUtcTime(), b.getSignedHeaders(), b.getSignature())
}

func (b *BaiduCloud) getCanonicalRequest() string {
	CanonicalUri := b.getCanonicalURI()
	CanonicalQueryString := b.getCanonicalQueryString()
	CanonicalHeaders := b.getCanonicalHeaders()
	return fmt.Sprintf("%s\n%s\n%s\n%s", b.Method, CanonicalUri, CanonicalQueryString, CanonicalHeaders)
}

func (b *BaiduCloud) getSignature() string {
	k := b.getSigningKey()
	str := b.getCanonicalRequest()
	return b.getHmacSha256(k, str)
}

func (b *BaiduCloud) getUtcTime() string {
	T := time.Now().UTC()
	return fmt.Sprintf("%04d-%02d-%02dT%02d:%02d:%02dZ", T.Year(), T.Month(), T.Day(), T.Hour(), T.Minute(), T.Second())
}

func (b *BaiduCloud) getHmacSha256(key string, str string) string {
	k := []byte(key)
	h := hmac.New(sha256.New, k)
	h.Write([]byte(str))

	sha := hex.EncodeToString(h.Sum(nil))
	// 返回字符串
	// s := base64.StdEncoding.EncodeToString([]byte(sha))
	return sha
}

func (b *BaiduCloud) getSigningKey() string {
	AuthStringPrefix := fmt.Sprintf("bce-auth-v1/%s/%s/%s", b.AccessKeyID, b.getUtcTime(), "1800")
	return b.getHmacSha256(b.AccessKeySecret, AuthStringPrefix)
}

func (b *BaiduCloud) getSignedHeaders() string {
	SignHeader := []string{"host", "content-md5", "content-length", "content-type"}
	var data []string
	for k := range b.Headers {
		if strings.HasPrefix(k, "x-bce-") || funk.Contains(SignHeader, strings.ToLower(k)) {
			data = append(data, strings.ToLower(k))
		}
	}
	sort.Strings(data)
	return strings.Join(data[:], ";")
}

func (b *BaiduCloud) getCanonicalHeaders() string {
	SignHeader := []string{"host", "content-md5", "content-length", "content-type"}
	var data []string
	for k, v := range b.Headers {
		if strings.HasPrefix(k, "x-bce-") || funk.Contains(SignHeader, strings.ToLower(k)) {
			data = append(data, fmt.Sprintf("%s:%s", urlEncode(strings.ToLower(k)), urlEncode(strings.TrimSpace(v))))
		}
	}
	sort.Strings(data)
	return strings.Join(data[:], "\n")
}

func (b *BaiduCloud) getCanonicalQueryString() string {
	up, err := urlParse(b.Url)
	if err != nil {
		logrus.Println("url parse解析异常: ", err)
	}
	if up.RawQuery != "" {
		var data []string
		for _, v := range strings.Split(up.RawQuery, "&") {
			s := strings.Split(v, "=")
			if len(s) < 2 && len(s) != 0 {
				data = append(data, fmt.Sprintf("%s=", urlEncode(s[0])))
			} else {
				data = append(data, fmt.Sprintf("%s=%s", urlEncode(s[0]), urlEncode(s[1])))
			}
		}
		sort.Strings(data)
		return strings.Join(data[:], "&")
	} else {
		return ""
	}
}

func (b *BaiduCloud) getCanonicalURI() string {
	up, err := urlParse(b.Url)
	if err != nil {
		logrus.Println("url parse解析异常: ", err)
	}
	if up.Path != "" {
		return up.Path
	} else {
		return "/"
	}

}

// url编码
func urlEncode(s string) string {
	return strings.Trim(fmt.Sprintln(url.QueryEscape(s)), "\n")
}

// url parse
func urlParse(u string) (*url.URL, error) {
	return url.Parse(u)
}
