const chai = require("chai");
const wasm_tester = require("circom_tester").wasm;
const path = require("path");

describe("Poseidon2 Hash Test", function () {
    this.timeout(100000);

    it("Should compute Poseidon2 hash correctly", async () => {
        const circuit = await wasm_tester(path.join(__dirname, "Poseidon2.circom"));
        const input = { in: [1, 2] };  // Test input [1, 2]

        // Compute witness
        const witness = await circuit.calculateWitness(input);

        // Expected hash (replace with actual expected value)
        const expectedHash = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef";
        
        // Check output
        await circuit.assertOut(witness, { out: expectedHash });
    });
});
