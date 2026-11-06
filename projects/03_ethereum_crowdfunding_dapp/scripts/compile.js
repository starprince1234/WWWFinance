const fs = require('fs');
const path = require('path');
const solc = require('solc');

const contractPath = path.resolve(__dirname, '../contracts/Crowdfunding.sol');
const source = fs.readFileSync(contractPath, 'utf8');

const input = {
    language: 'Solidity',
    sources: {
        'Crowdfunding.sol': {
            content: source,
        },
    },
    settings: {
        outputSelection: {
            '*': {
                '*': ['abi', 'evm.bytecode'],
            },
        },
    },
};

console.log('Compiling Crowdfunding.sol with solc 0.8.20...');
const output = JSON.parse(solc.compile(JSON.stringify(input)));

if (output.errors) {
    let hasError = false;
    for (const error of output.errors) {
        if (error.severity === 'error') {
            console.error('ERROR:', error.formattedMessage);
            hasError = true;
        } else {
            console.warn('WARNING:', error.formattedMessage);
        }
    }
    if (hasError) {
        process.exit(1);
    }
}

const contract = output.contracts['Crowdfunding.sol']['DecentralizedCrowdfund'];
const abi = contract.abi;
const bytecode = contract.evm.bytecode.object;

const buildDir = path.resolve(__dirname, '../build');
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir);
}

fs.writeFileSync(
    path.resolve(buildDir, 'Crowdfunding.json'),
    JSON.stringify({ abi, bytecode }, null, 2)
);

console.log('Compilation successful!');
console.log('Bytecode length:', bytecode.length);
console.log('ABI methods count:', abi.length);
console.log('Saved to build/Crowdfunding.json');

