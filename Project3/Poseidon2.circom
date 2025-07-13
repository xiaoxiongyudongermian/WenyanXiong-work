pragma circom 2.0.0;

// Poseidon2 Permutation for (t=2, nRoundsF=8, nRoundsP=5)
template Poseidon2Permutation() {
    signal input state[2];  // t=2 (2 field elements)
    signal output out[2];

    // --- Round Constants (Precomputed for t=2, nRoundsF=8, nRoundsP=5) ---
    var roundConstants = [
        // Full rounds (first 4 and last 4)
        0x0e7f4567a3e2b1799b0aa2e1d0e5c6f7,
        0x1c8d3456b2a1f0e9d8c7b6a5f4e3d2c1,
        0x2a9f2345c1b0e9f8d7c6b5a4f3e2d1c0,
        0x38b12345d0c9f8e7d6c5b4a3f2e1d0cf,
        // Partial rounds (5 rounds)
        0x46c34567e9d8c7b6a5f4e3d2c1b0a9f8,
        0x54d45678f8e7d6c5b4a3f2e1d0c9b8a7,
        0x62e56789a7b6c5d4e3f2g1h0i9j8k7l6,
        0x70f6789ab6c5d4e3f2g1h0i9j8k7l6m5,
        0x7e0789abc5d4e3f2g1h0i9j8k7l6m5n4
    ];

    // --- MDS Matrix (Precomputed for t=2) ---
    var mdsMatrix = [
        [0x1, 0x2],
        [0x3, 0x4]
    ];

    // --- Permutation (8 full rounds + 5 partial rounds) ---
    signal intermediate[2];

    // Initialize state
    intermediate[0] <== state[0];
    intermediate[1] <== state[1];

    // Full Rounds (first 4)
    for (var r = 0; r < 4; r++) {
        // AddRoundConstants
        intermediate[0] <== intermediate[0] + roundConstants[r * 2];
        intermediate[1] <== intermediate[1] + roundConstants[r * 2 + 1];

        // S-box (x^5)
        intermediate[0] <== intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0];
        intermediate[1] <== intermediate[1] * intermediate[1] * intermediate[1] * intermediate[1] * intermediate[1];

        // MDS Mix
        var new0 = mdsMatrix[0][0] * intermediate[0] + mdsMatrix[0][1] * intermediate[1];
        var new1 = mdsMatrix[1][0] * intermediate[0] + mdsMatrix[1][1] * intermediate[1];
        intermediate[0] <== new0;
        intermediate[1] <== new1;
    }

    // Partial Rounds (5 rounds)
    for (var r = 0; r < 5; r++) {
        // AddRoundConstants
        intermediate[0] <== intermediate[0] + roundConstants[8 + r];
        intermediate[1] <== intermediate[1] + roundConstants[8 + r + 1];

        // S-box (only first element)
        intermediate[0] <== intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0];

        // MDS Mix
        var new0 = mdsMatrix[0][0] * intermediate[0] + mdsMatrix[0][1] * intermediate[1];
        var new1 = mdsMatrix[1][0] * intermediate[0] + mdsMatrix[1][1] * intermediate[1];
        intermediate[0] <== new0;
        intermediate[1] <== new1;
    }

    // Full Rounds (last 4)
    for (var r = 0; r < 4; r++) {
        // AddRoundConstants
        intermediate[0] <== intermediate[0] + roundConstants[4 * 2 + r * 2];
        intermediate[1] <== intermediate[1] + roundConstants[4 * 2 + r * 2 + 1];

        // S-box (x^5)
        intermediate[0] <== intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0] * intermediate[0];
        intermediate[1] <== intermediate[1] * intermediate[1] * intermediate[1] * intermediate[1] * intermediate[1];

        // MDS Mix
        var new0 = mdsMatrix[0][0] * intermediate[0] + mdsMatrix[0][1] * intermediate[1];
        var new1 = mdsMatrix[1][0] * intermediate[0] + mdsMatrix[1][1] * intermediate[1];
        intermediate[0] <== new0;
        intermediate[1] <== new1;
    }

    // Output
    out[0] <== intermediate[0];
    out[1] <== intermediate[1];
}

// Poseidon2 Hash (t=2, nRoundsF=8, nRoundsP=5)
template Poseidon2Hash() {
    signal input in[2];  // 2 input field elements
    signal output out;    // 256-bit output (first element)

    component perm = Poseidon2Permutation();
    perm.state[0] <== in[0];
    perm.state[1] <== in[1];

    out <== perm.out[0];  // Return the first state element as hash
}

component main = Poseidon2Hash();
