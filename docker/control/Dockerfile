from tchimenti/node-custom-mallory

# # we don't want to download the dependencies on every run
COPY jepsen/jepsen/project.clj /jepsen/jepsen/project.clj
RUN if [ -f /jepsen/jepsen/project.clj ]; then cd /jepsen/jepsen && lein deps; fi

# actually install
COPY jepsen/jepsen /jepsen/jepsen/
RUN if [ -f /jepsen/jepsen/project.clj ]; then cd /jepsen/jepsen && lein install; fi
COPY jepsen /jepsen/

ADD ./bashrc /root/.bashrc
ADD ./init.sh /init.sh
RUN dos2unix /init.sh /root/.bashrc \
    && chmod +x /init.sh

CMD /init.sh
