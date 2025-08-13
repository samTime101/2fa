const now = new Date();
const minute = now.getUTCMinutes();

now.setUTCSeconds(0, 0); 
const timestampStr = now.toISOString().split('.')[0] + 'Z';

console.log(minute, timestampStr);
