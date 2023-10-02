import { useRef } from 'react';

let symmetric;
let room_symmetric;
let keyPair;

export const InitializeCryptoState = () => {
    symmetric = useRef(null);
    room_symmetric = useRef(null);
    keyPair = useRef(null);
}

export const GlobalCryptoState = {
    setSymmetric(sym) {
        symmetric.current = sym;
    },
    getSymmetric() {
        return symmetric.current;
    },
    setRoomSymmetric(sym) {
        room_symmetric.current = sym;
    },
    getRoomSymmetric() {
        return room_symmetric.current;
    },
    setKeyPair(kp) {
        keyPair = kp;
    },
    getKeyPair() {
        return keyPair;
    }
}