const supabaseAuthClient =
    window.supabase.createClient(
        window.KRISHISAATHI_SUPABASE_URL,
        window.KRISHISAATHI_SUPABASE_KEY
    );


// ==========================================
// CHECK LOGIN
// ==========================================

async function checkKrishiSaathiLogin() {

    const {
        data,
        error
    } = await supabaseAuthClient.auth.getSession();

    if (error || !data.session) {

        window.location.href = "/login";

        return null;
    }

    return data.session;

}


// ==========================================
// LOGOUT
// ==========================================

async function krishiSaathiLogout() {

    await supabaseAuthClient.auth.signOut();

    window.location.href = "/login";

}


// ==========================================
// CURRENT USER
// ==========================================

async function getKrishiSaathiUser() {

    const {
        data
    } = await supabaseAuthClient.auth.getUser();

    return data.user;

}


// ==========================================
// ACCESS TOKEN
// ==========================================

async function getKrishiSaathiToken() {

    const {
        data
    } = await supabaseAuthClient.auth.getSession();

    if (!data.session) {

        window.location.href = "/login";

        return null;
    }

    return data.session.access_token;

}
