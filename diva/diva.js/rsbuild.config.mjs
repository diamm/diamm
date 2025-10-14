import { defineConfig } from '@rsbuild/core';
import { pluginSass } from '@rsbuild/plugin-sass';


export default defineConfig({
    plugins: [pluginSass()],
    source: {
        entry: {
            diva: ["./source/js/diva.ts", "./source/css/diva.scss"],
        }
    },
    server: {
        port: 9001
    },
    output: {
        copy: [
            {from: './source/js/plugins', to: 'static/js/plugins'},
        ],
        filenameHash: false
    },
    html: {
        template: "./index.html"
    },
    tools: {
        rspack: {}
    }
});
