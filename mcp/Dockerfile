ARG LEO_BBS_NODE_IMAGE=node:22-bookworm-slim
FROM ${LEO_BBS_NODE_IMAGE}
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY server.js ./
USER node
ENTRYPOINT ["node", "server.js"]
