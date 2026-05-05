const firebaseConfig = {
    apiKey: "AIzaSyASlD4FM6lyIEzBAzPlflhlCwDc3Toh6Fo",
    authDomain: "earning-a9b0c.firebaseapp.com",
    databaseURL: "https://earning-a9b0c-default-rtdb.firebaseio.com",
    projectId: "earning-a9b0c"
};

if (!firebase.apps.length) { firebase.initializeApp(firebaseConfig); }
const auth = firebase.auth();
const db = firebase.database();
const DB_ROOT = 'Bankey_BG_System';
