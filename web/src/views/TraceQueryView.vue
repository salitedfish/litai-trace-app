<template>
  <div class="h-full flex flex-col relative z-10 w-full max-w-[1400px] mx-auto pt-4">
    <!-- 搜索区 -->
    <div class="bg-card rounded-xl border border-border/40 p-3 shadow-sm mb-3 shrink-0">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="flex items-center gap-2">
          <span class="text-xs font-medium text-muted-foreground shrink-0 w-16">产出码</span>
          <input v-model="outputCode" type="text" placeholder="输入产出码追溯"
            class="flex-1 px-3 py-1.5 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all"
            @keyup.enter="handleOutputSearch" />
          <button class="px-3 py-1.5 bg-accent text-white rounded-lg text-xs font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 shrink-0" :disabled="outputLoading || !outputCode.trim()" @click="handleOutputSearch">
            <svg v-if="outputLoading" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-medium text-muted-foreground shrink-0 w-16">投入码</span>
          <input v-model="inputCode" type="text" placeholder="输入投入码查询关联产出"
            class="flex-1 px-3 py-1.5 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent transition-all"
            @keyup.enter="handleInputSearch" />
          <button class="px-3 py-1.5 bg-accent text-white rounded-lg text-xs font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 shrink-0" :disabled="inputLoading || !inputCode.trim()" @click="handleInputSearch">
            <svg v-if="inputLoading" class="animate-spin w-3.5 h-3.5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-show="searched" class="bg-card rounded-xl border border-border/40 shadow-sm flex flex-col flex-1 min-h-0">
      <div class="px-4 py-2 border-b border-border/40 bg-muted/20 flex items-center justify-between shrink-0">
        <span class="text-sm text-muted-foreground">
          <template v-if="traceSteps.length > 0">
            追溯链路共 <strong class="text-foreground">{{ traceSteps.length }}</strong> 步
          </template>
          <template v-else>
            未找到追溯链路
          </template>
          <span v-if="searchedCode" class="ml-2 text-xs">— 追溯码: <code class="bg-muted px-1.5 py-0.5 rounded text-accent">{{ searchedCode }}</code></span>
        </span>
      </div>

      <div v-if="traceSteps.length === 0 && !searchError" class="py-8 text-center text-muted-foreground shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>未找到该产出码的追溯记录</p>
      </div>

      <div v-if="searchError" class="py-8 text-center shrink-0">
        <svg class="w-12 h-12 mx-auto mb-3 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-red-500 font-medium">{{ searchError }}</p>
      </div>

      <div v-else class="overflow-auto flex-1 min-h-0">
        <table class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-muted/50 z-10">
            <tr class="border-b border-border text-xs uppercase tracking-wider text-muted-foreground">
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-12 text-center">#</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">工序编码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">工序名称</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">物料编码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">物料类型</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">条码</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作时间</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">设备名称</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">检测结果</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap">操作人</th>
              <th class="px-3 py-2.5 font-semibold whitespace-nowrap w-64 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/50 text-sm">
            <tr v-for="(step, idx) in traceSteps" :key="step.workorder_code + '-' + idx"
              class="hover:bg-accent/5 transition-colors"
              :class="{'bg-muted/10': step.level > 0}">
              <td class="px-3 py-2.5 text-center">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded text-xs font-bold" :class="stepBadgeClass(step)">{{ idx + 1 }}</span>
              </td>
              <td class="px-3 py-2.5 font-mono text-xs">{{ step.procedure_code }}</td>
              <td class="px-3 py-2.5 text-sm">{{ step.procedure_name || '-' }}</td>
              <td class="px-3 py-2.5 font-mono text-xs">{{ step.material_code }}</td>
              <td class="px-3 py-2.5"><material-type-tag :type="step.material_type" /></td>
              <td class="px-3 py-2.5 font-mono text-xs max-w-[180px] truncate" :title="step.qr_code">{{ step.qr_code }}</td>
              <td class="px-3 py-2.5 text-muted-foreground text-xs">{{ fmtTime(step.op_time) }}</td>
              <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ step.device_name || step.device_code || '-' }}</td>
              <td class="px-3 py-2.5"><span :class="checkResultClass(step.check_result)">{{ step.check_result || '-' }}</span></td>
              <td class="px-3 py-2.5 text-sm">{{ step.operator }}</td>
              <td class="px-3 py-2.5 text-center">
                <div class="flex items-center justify-center gap-1.5">
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openInputModal(step)">查看投入</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openProcessParamModal(step)">工艺参数</button>
                  <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-purple-50 text-purple-600 hover:bg-purple-100 border border-purple-200 transition-colors" @click="openSubmissionModal(step)">提交记录</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 投入物料弹窗 -->
    <transition name="modal-fade">
      <div v-if="inputModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeInputModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">投入物料明细</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ modalStep?.procedure_name || '工序' }}
                <span v-if="modalStep?.procedure_code" class="ml-1 font-mono">({{ modalStep?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ modalStep?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeInputModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="modalLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="modalError" class="text-sm text-red-500 py-4 text-center">{{ modalError }}</div>
            <div v-else-if="modalInputs.length === 0" class="text-sm text-muted-foreground py-8 text-center">该次报工无投入记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-[120px]">物料编码</th>
                    <th class="px-3 py-2.5 font-medium w-20">物料类型</th>
                    <th class="px-3 py-2.5 font-medium">条码</th>
                    <th class="px-3 py-2.5 font-medium w-12 text-center">数量</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(input, i) in modalInputs" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 font-mono text-xs">{{ input.material_code }}</td>
                    <td class="px-3 py-2.5"><material-type-tag :type="input.material_type" /></td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[200px] truncate" :title="input.qr_code">{{ input.qr_code }}</td>
                    <td class="px-3 py-2.5 text-center">{{ input.require_num }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(input.op_time) }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <button class="px-2 py-1 rounded text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors"
                        @click="traceInputCode(input.qr_code)">追溯此码</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 工艺参数弹窗 -->
    <transition name="modal-fade">
      <div v-if="paramModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeParamModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">工艺参数</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ paramStep?.procedure_name || '工序' }}
                <span v-if="paramStep?.procedure_code" class="ml-1 font-mono">({{ paramStep?.procedure_code }})</span>
                <span class="ml-2">产出: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ paramStep?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeParamModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="paramLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="paramError" class="text-sm text-red-500 py-4 text-center">{{ paramError }}</div>
            <div v-else-if="paramData.length === 0" class="text-sm text-muted-foreground py-8 text-center">该工单无工艺参数数据</div>
            <div v-else class="space-y-4">
              <div v-for="(item, idx) in paramData" :key="idx" class="rounded-lg border border-border/50 bg-muted/10 p-4">
                <div class="flex items-center justify-between mb-2 text-xs text-muted-foreground">
                  <span class="font-medium">{{ item.device_name || item.device_code }} — {{ item.procedure_name }}</span>
                  <span>{{ fmtTime(item.timestamp) }}</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                  <div v-for="(val, key) in item.params" :key="key" class="bg-white rounded border border-border/40 px-3 py-2">
                    <p class="text-[10px] text-muted-foreground font-mono">{{ key }}</p>
                    <p class="text-sm font-semibold text-foreground">{{ val }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 提交记录弹窗 -->
    <transition name="modal-fade">
      <div v-if="subModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeSubModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">提交记录</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ subStep?.procedure_name || '工序' }}
                <span v-if="subStep?.procedure_code" class="ml-1 font-mono">({{ subStep?.procedure_code }})</span>
                <span class="ml-2">条码: <code class="bg-muted px-1 py-0.5 rounded font-mono text-xs">{{ subStep?.qr_code }}</code></span>
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeSubModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="subLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              加载中...
            </div>
            <div v-else-if="subError" class="text-sm text-red-500 py-4 text-center">{{ subError }}</div>
            <div v-else-if="subRecords.length === 0" class="text-sm text-muted-foreground py-8 text-center">无提交记录</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">工单编码</th>
                    <th class="px-3 py-2.5 font-medium w-36">操作时间</th>
                    <th class="px-3 py-2.5 font-medium">操作人</th>
                    <th class="px-3 py-2.5 font-medium">检测结果</th>
                    <th class="px-3 py-2.5 font-medium w-44 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(rec, i) in subRecords" :key="i" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[250px] truncate" :title="rec.workorder_code">{{ rec.workorder_code }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(rec.op_time) }}</td>
                    <td class="px-3 py-2.5">{{ rec.operator }}</td>
                    <td class="px-3 py-2.5"><span class="text-xs" :class="checkResultClass(rec.check_result)">{{ rec.check_result || '-' }}</span></td>
                    <td class="px-3 py-2.5 text-center">
                      <div class="flex items-center justify-center gap-1.5">
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" @click="openInputModal({ workorder_code: rec.workorder_code, procedure_name: subStep?.procedure_name, procedure_code: subStep?.procedure_code, qr_code: subStep?.qr_code })">查看投入</button>
                        <button class="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-200 transition-colors" @click="openProcessParamModal({ workorder_code: rec.workorder_code, procedure_name: subStep?.procedure_name, procedure_code: subStep?.procedure_code, qr_code: subStep?.qr_code })">工艺参数</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 投入码选产出的弹窗 -->
    <transition name="modal-fade">
      <div v-if="inputCodeModalVisible" class="fixed inset-0 z-[1000] flex items-center justify-center bg-black/30" @click.self="closeInputCodeModal">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden transform transition-all border border-border flex flex-col m-4">
          <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between shrink-0 bg-muted/10">
            <div>
              <h3 class="text-base font-bold text-foreground">选择产出码</h3>
              <p class="text-xs text-muted-foreground mt-0.5">
                投入码 <code class="bg-muted px-1 py-0.5 rounded font-mono">{{ inputCode }}</code> 关联了以下产出码，请选择一条进行追溯
              </p>
            </div>
            <button class="p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors" @click="closeInputCodeModal">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="overflow-auto flex-1 p-6">
            <div v-if="inputCodeLoading" class="flex items-center justify-center gap-2 text-sm text-muted-foreground py-8">
              <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
              查询中...
            </div>
            <div v-else-if="inputCodeError" class="text-sm text-red-500 py-4 text-center">{{ inputCodeError }}</div>
            <div v-else-if="inputCodeOptions.length === 0" class="text-sm text-muted-foreground py-8 text-center">未找到关联的产出码</div>
            <div v-else>
              <table class="w-full text-left border-collapse text-sm">
                <thead>
                  <tr class="border-b border-border/50 text-xs text-muted-foreground">
                    <th class="px-3 py-2.5 font-medium w-14 text-center">#</th>
                    <th class="px-3 py-2.5 font-medium">工序名称</th>
                    <th class="px-3 py-2.5 font-medium">物料编码</th>
                    <th class="px-3 py-2.5 font-medium">物料类型</th>
                    <th class="px-3 py-2.5 font-medium">产出码</th>
                    <th class="px-3 py-2.5 font-medium">操作时间</th>
                    <th class="px-3 py-2.5 font-medium w-24 text-center">操作</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/30">
                  <tr v-for="(opt, i) in inputCodeOptions" :key="opt.qr_code" class="hover:bg-muted/30">
                    <td class="px-3 py-2.5 text-center text-muted-foreground">{{ i + 1 }}</td>
                    <td class="px-3 py-2.5">{{ opt.procedure_name || '-' }}</td>
                    <td class="px-3 py-2.5 font-mono text-xs">{{ opt.material_code }}</td>
                    <td class="px-3 py-2.5"><material-type-tag :type="opt.material_type" /></td>
                    <td class="px-3 py-2.5 font-mono text-xs max-w-[200px] truncate" :title="opt.qr_code">{{ opt.qr_code }}</td>
                    <td class="px-3 py-2.5 text-xs text-muted-foreground">{{ fmtTime(opt.op_time) }}</td>
                    <td class="px-3 py-2.5 text-center">
                      <button class="px-3 py-1.5 rounded-md text-xs font-medium bg-accent text-white hover:bg-accent/90 transition-colors" @click="selectInputCodeOutput(opt)">选择</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h } from 'vue'
import api from '../api/trace-app'

const outputCode = ref('')
const inputCode = ref('')
const searchedCode = ref('')
const outputLoading = ref(false)
const inputLoading = ref(false)
const searched = ref(false)
const searchError = ref('')
const traceSteps = ref<any[]>([])

// 投入物料弹窗
const inputModalVisible = ref(false)
const modalStep = ref<any>(null)
const modalInputs = ref<any[]>([])
const modalLoading = ref(false)
const modalError = ref('')

// 工艺参数弹窗
const paramModalVisible = ref(false)
const paramStep = ref<any>(null)
const paramData = ref<any[]>([])
const paramLoading = ref(false)
const paramError = ref('')

// 提交记录弹窗
const subModalVisible = ref(false)
const subStep = ref<any>(null)
const subRecords = ref<any[]>([])
const subLoading = ref(false)
const subError = ref('')

// 投入码选择弹窗
const inputCodeModalVisible = ref(false)
const inputCodeLoading = ref(false)
const inputCodeError = ref('')
const inputCodeOptions = ref<any[]>([])

// ========== 产出码追溯 ==========
const handleOutputSearch = async () => {
  const code = outputCode.value.trim()
  if (!code) return
  traceSteps.value = []
  searched.value = false
  searchError.value = ''
  outputLoading.value = true
  searchedCode.value = code
  try {
    const res = await api.queryByOutput(code)
    traceSteps.value = res.data || []
    searched.value = true
    searchError.value = ''
  } catch (err: any) {
    console.error('查询失败:', err)
    traceSteps.value = []
    searchError.value = '查询失败，请检查网络或稍后重试'
  } finally {
    outputLoading.value = false
  }
}

// ========== 投入码追溯 ==========
const handleInputSearch = async () => {
  const code = inputCode.value.trim()
  if (!code) return
  await queryInputCodeOutputs(code)
}

// ========== 投入码查询 ==========
const queryInputCodeOutputs = async (code: string) => {
  inputCodeModalVisible.value = true
  inputCodeLoading.value = true
  inputCodeError.value = ''
  inputCodeOptions.value = []
  try {
    const res = await api.queryOutputsByInput(code)
    inputCodeOptions.value = res.data || []
  } catch (err: any) {
    inputCodeError.value = '查询失败: ' + (err?.message || '未知错误')
  } finally {
    inputCodeLoading.value = false
  }
}

const closeInputCodeModal = () => {
  inputCodeModalVisible.value = false
}

const selectInputCodeOutput = (opt: any) => {
  inputCodeModalVisible.value = false
  outputCode.value = opt.qr_code
  searchedCode.value = opt.qr_code
  handleOutputSearch()
}

// ========== 投入弹窗 ==========
const openInputModal = async (step: any) => {
  modalStep.value = step
  inputModalVisible.value = true
  modalLoading.value = true
  modalError.value = ''
  modalInputs.value = []
  try {
    const res = await api.queryInputs(step.workorder_code)
    modalInputs.value = res.data || []
  } catch (err: any) {
    modalError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    modalLoading.value = false
  }
}

const closeInputModal = () => {
  inputModalVisible.value = false
  modalStep.value = null
  modalInputs.value = []
}

const traceInputCode = (qrCode: string) => {
  closeInputModal()
  inputCode.value = qrCode
  handleInputSearch()
}

// ========== 工艺参数弹窗 ==========
const openProcessParamModal = async (step: any) => {
  paramStep.value = step
  paramModalVisible.value = true
  paramLoading.value = true
  paramError.value = ''
  paramData.value = []
  try {
    const res = await api.queryProcessParams(step.workorder_code)
    paramData.value = res.data || []
  } catch (err: any) {
    paramError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    paramLoading.value = false
  }
}

const closeParamModal = () => {
  paramModalVisible.value = false
  paramStep.value = null
  paramData.value = []
}

// ========== 提交记录弹窗 ==========
const openSubmissionModal = async (step: any) => {
  subStep.value = step
  subModalVisible.value = true
  subLoading.value = true
  subError.value = ''
  subRecords.value = []
  try {
    const res = await api.querySubmissionRecords(step.qr_code, step.procedure_code, step.device_code)
    subRecords.value = res.data || []
  } catch (err: any) {
    subError.value = '加载失败: ' + (err?.message || '未知错误')
  } finally {
    subLoading.value = false
  }
}

const closeSubModal = () => {
  subModalVisible.value = false
  subStep.value = null
  subRecords.value = []
}

// ========== 工具 ==========
const fmtTime = (t: string) => t ? t.replace(/\.\d+$/, '') : '-'

const checkResultClass = (v: string) => {
  if (!v || v === '-') return ''
  if (v === '一次合格' || v === 'OK') return 'text-teal-600 font-medium'
  if (v === '返工合格') return 'text-amber-600 font-medium'
  if (v === '复投合格') return 'text-blue-600 font-medium'
  return 'text-red-600 font-medium'
}

const stepBadgeClass = (step: any) => {
  const t = step.material_type
  if (t === 'finished_product') return 'bg-teal-100 text-teal-700'
  if (t === 'semi_finished_product') return 'bg-blue-100 text-blue-700'
  if (t === 'raw_material') return 'bg-amber-100 text-amber-700'
  return 'bg-muted text-muted-foreground'
}

// 物料类型标签组件
const MaterialTypeTag = defineComponent({
  name: 'MaterialTypeTag',
  props: { type: String },
  setup(props: any) {
    const labels: Record<string, string> = {
      raw_material: '原材料',
      semi_finished_product: '半成品',
      finished_product: '成品',
    }
    const colors: Record<string, string> = {
      raw_material: 'bg-amber-50 text-amber-600 border-amber-200',
      semi_finished_product: 'bg-blue-50 text-blue-600 border-blue-200',
      finished_product: 'bg-teal-50 text-teal-600 border-teal-200',
    }
    return () => {
      const type = props.type || ''
      const label = labels[type] || type
      const color = colors[type] || 'bg-gray-50 text-gray-600 border-gray-200'
      return h('span', {
        class: `inline-block px-2 py-0.5 rounded text-xs font-medium border ${color}`
      }, label)
    }
  }
})
</script>

<style scoped>
.modal-fade-enter-active {
  transition: opacity 0.15s ease-out;
}
.modal-fade-leave-active {
  transition: opacity 0.1s ease-in;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
