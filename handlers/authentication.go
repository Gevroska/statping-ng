package handlers

import (
	"crypto/subtle"
	"github.com/Gevroska/statping-ng/types/core"
	"github.com/Gevroska/statping-ng/types/users"
	"github.com/Gevroska/statping-ng/utils"
	"net/http"
	"strings"
)

// hasSetupEnv checks to see if the GO_ENV is set to 'true'
// or if the Statping instance has not been setup yet
func hasSetupEnv() bool {
	if utils.Params.Get("GO_ENV") == "test" {
		return true
	}
	if core.App == nil {
		return true
	}
	if !core.App.Setup {
		return false
	}
	return false
}

// apiQueryScope returns the privileges granted by the `api` query parameter.
func apiQueryScope(r *http.Request) string {
	query := r.URL.Query()
	key := query.Get("api")
	if key == "" {
		return ""
	}
	if subtle.ConstantTimeCompare([]byte(key), []byte(core.App.ApiSecret)) == 1 {
		return "admin"
	}
	// A user's API key must not grant more privileges than that user has.
	user, err := users.FindByAPIKey(key)
	if err != nil {
		return ""
	}
	if subtle.ConstantTimeCompare([]byte(key), []byte(user.ApiKey)) == 1 {
		if user.Admin.Valid && user.Admin.Bool {
			return "admin"
		}
		return "user"
	}
	return ""
}

// hasAuthorizationHeader check to see if the Authorization header is the correct API Secret Key
func hasAuthorizationHeader(r *http.Request) bool {
	var token string
	tokens, ok := r.Header["Authorization"]
	if ok && len(tokens) >= 1 {
		token = tokens[0]
		token = strings.TrimPrefix(token, "Bearer ")
		if subtle.ConstantTimeCompare([]byte(token), []byte(core.App.ApiSecret)) == 1 {
			return true
		}
	}
	return false
}
