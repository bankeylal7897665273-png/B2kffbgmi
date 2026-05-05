const firebaseConfig = {
    apiKey: "AIzaSyASlD4FM6lyIEzBAzPlflhlCwDc3Toh6Fo",
    authDomain: "earning-a9b0c.firebaseapp.com",
    databaseURL: "https://earning-a9b0c-default-rtdb.firebaseio.com",
    projectId: "earning-a9b0c",
    storageBucket: "earning-a9b0c.firebasestorage.app",
    messagingSenderId: "543786047307",
    appId: "1:543786047307:web:4d3d9382359c7383fd3ace"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.database();
const DB_ROOT = 'BG_Remover_System';
