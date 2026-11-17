ARG LEO_BBS_NODE_IMAGE=node:22-bookworm-slim
FROM ${LEO_BBS_NODE_IMAGE}
WORKDIR /app
COPY --chmod=644 package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --chmod=644 server.js forum-server.js http.js http-server.js ./
USER node
ENTRYPOINT ["node", "server.js"]
